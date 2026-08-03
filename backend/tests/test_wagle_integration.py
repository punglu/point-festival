"""PHASE2-WAGLE-FOUNDATION-R2A-REPAIR-001 real-PostgreSQL integration and
concurrency suite. Targets the isolated Phase 2 fixture database only.

Covers the 12 required items from the R2-A TEST COMPLETION handoff:
  1  unauthenticated / cross-family / non-participant denial (+ DB invariance)
  2  DIRECT canonical pair concurrent creation
  3  message sequence concurrent creation
  4  same client_message_id + same payload concurrent send (idempotency)
  5  same client_message_id + different payload -> 409, DB invariant
  6  read-state concurrent update -> monotonic non-regression
  7  TEXT body boundary 4000 / 4001
  8  client_message_id boundary 64 / 65
  9  pagination default 50 / max 100 / 101 rejected
  10 GROUP active participant cap 50 / 51
  11 cursor pagination: no duplicates, no gaps across a large volume
  12 LEFT / REMOVED / subscription-read-only visibility and write boundaries
"""
from __future__ import annotations

from sqlalchemy import text

from app.domains.wagle.board_constants import FAMILY_BOARD_ROOM_TITLE
from tests.conftest import create_actor, create_bare_membership, create_family, run_concurrent, set_subscription


async def _counts(db, *tables: str) -> dict[str, int]:
    out = {}
    for t in tables:
        out[t] = (await db.execute(text(f"SELECT count(*) FROM {t}"))).scalar_one()
    return out


# ---------------------------------------------------------------------------
# 1. unauthenticated / cross-family / non-participant denial
# ---------------------------------------------------------------------------

async def test_01a_unauthenticated_request_denied(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    before = await _counts(db, "wagle_rooms")
    resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": family_env["member"].membership_id},
    )
    assert resp.status_code == 401
    after = await _counts(db, "wagle_rooms")
    assert before == after


async def test_01a_invalid_token_denied(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    before = await _counts(db, "wagle_rooms")
    resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": family_env["member"].membership_id},
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert resp.status_code == 401
    after = await _counts(db, "wagle_rooms")
    assert before == after


async def test_01b_cross_family_access_denied(family_env):
    client, db = family_env["client"], family_env["db"]
    other_family = await create_family(db, "Other Family")
    outsider = await create_actor(db, other_family, name="outsider", service_role="participant")
    await set_subscription(db, other_family, "active")

    room_resp = await client.post(
        f"/api/families/{family_env['family_id']}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": family_env["member"].membership_id},
        headers=family_env["admin"].headers,
    )
    room_id = room_resp.json()["id"]

    before = await _counts(db, "wagle_messages")
    resp = await client.get(
        f"/api/families/{family_env['family_id']}/wagle/rooms/{room_id}/messages",
        headers=outsider.headers,
    )
    assert resp.status_code == 403
    after = await _counts(db, "wagle_messages")
    assert before == after


async def test_01c_non_participant_denied(family_env):
    """Same family, has a Wagle role, but was never added to this room."""
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    bystander = await create_actor(db, family_id, name="bystander", service_role="participant")

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": family_env["member"].membership_id},
        headers=family_env["admin"].headers,
    )
    room_id = room_resp.json()["id"]

    resp = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        headers=bystander.headers,
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 2. DIRECT canonical pair concurrent creation
# ---------------------------------------------------------------------------

async def test_02_direct_canonical_concurrent_creation(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    async def create_from_admin():
        return await client.post(
            f"/api/families/{family_id}/wagle/rooms",
            json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
            headers=admin.headers,
        )

    results = await run_concurrent([create_from_admin for _ in range(6)])

    assert all(not isinstance(r, Exception) for r in results)
    statuses = [r.status_code for r in results]
    assert all(s == 201 for s in statuses), statuses

    room_ids = {r.json()["id"] for r in results}
    assert len(room_ids) == 1, "concurrent DIRECT creation must converge on one room"

    counts = await _counts(db, "wagle_rooms", "wagle_direct_pairs")
    assert counts["wagle_rooms"] == 1
    assert counts["wagle_direct_pairs"] == 1


# ---------------------------------------------------------------------------
# 2b. Family-board (reserved GROUP sentinel) concurrent creation --
# RE-QA-F-BOARD-ROOM-RACE regression (migration 0021 +
# create_room's GROUP-branch get-or-create). 5 concurrent requests x 10
# iterations, a fresh Family each iteration so every iteration is a genuine
# first-creation race (an already-existing board room would only exercise
# the cheap read path, not the race window this defect lived in).
# ---------------------------------------------------------------------------

async def test_02b_family_board_concurrent_creation_converges_on_one_room(family_env):
    client, db = family_env["client"], family_env["db"]

    for i in range(10):
        family_id = await create_family(db, name=f"Board Race Family {i}")
        admin = await create_actor(db, family_id, name=f"board-admin-{i}", service_role="room_admin")
        await set_subscription(db, family_id, "active")

        async def create_board():
            return await client.post(
                f"/api/families/{family_id}/wagle/rooms",
                json={"room_type": "GROUP", "title": FAMILY_BOARD_ROOM_TITLE, "participant_membership_ids": []},
                headers=admin.headers,
            )

        results = await run_concurrent([create_board for _ in range(5)])

        assert all(not isinstance(r, Exception) for r in results), results
        statuses = [r.status_code for r in results]
        assert all(s == 201 for s in statuses), statuses

        room_ids = {r.json()["id"] for r in results}
        assert len(room_ids) == 1, f"iteration {i}: concurrent board creation must converge on one room, got {room_ids}"

        count = (
            await db.execute(
                text(
                    "SELECT count(*) FROM wagle_rooms WHERE family_group_id = :fid "
                    "AND title = :title AND room_type = 'GROUP' AND deleted_at IS NULL"
                ),
                {"fid": family_id, "title": FAMILY_BOARD_ROOM_TITLE},
            )
        ).scalar_one()
        assert count == 1, f"iteration {i}: exactly one board room must persist per family, found {count}"


# ---------------------------------------------------------------------------
# 3. message sequence concurrent creation
# ---------------------------------------------------------------------------

async def test_03_message_sequence_concurrent_creation(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    n = 20

    def factory(i, actor):
        async def send():
            return await client.post(
                f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
                json={"client_message_id": f"seq-{i}", "body": f"message {i}"},
                headers=actor.headers,
            )

        return send

    factories = [factory(i, admin if i % 2 == 0 else member) for i in range(n)]
    results = await run_concurrent(factories)

    assert all(not isinstance(r, Exception) for r in results)
    assert all(r.status_code == 201 for r in results), [r.status_code for r in results]

    sequences = sorted(r.json()["sequence"] for r in results)
    assert sequences == list(range(1, n + 1)), sequences

    count = (
        await db.execute(text("SELECT count(*) FROM wagle_messages WHERE room_id = :rid"), {"rid": room_id})
    ).scalar_one()
    assert count == n


# ---------------------------------------------------------------------------
# 4 & 5. client_message_id idempotency
# ---------------------------------------------------------------------------

async def test_04_same_client_id_same_payload_concurrent_idempotent(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    async def send():
        return await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"client_message_id": "idem-1", "body": "same payload"},
            headers=admin.headers,
        )

    results = await run_concurrent([send for _ in range(8)])

    assert all(not isinstance(r, Exception) for r in results), results
    assert all(r.status_code != 500 for r in results), [r.status_code for r in results]
    assert all(r.status_code == 201 for r in results), [r.status_code for r in results]

    message_ids = {r.json()["id"] for r in results}
    sequences = {r.json()["sequence"] for r in results}
    assert len(message_ids) == 1, f"expected one converged message id, got {message_ids}"
    assert len(sequences) == 1, f"expected one converged sequence, got {sequences}"

    row_count = (
        await db.execute(
            text(
                "SELECT count(*) FROM wagle_messages WHERE room_id = :rid AND client_message_id = 'idem-1'"
            ),
            {"rid": room_id},
        )
    ).scalar_one()
    assert row_count == 1


async def test_05_same_client_id_different_payload_conflict_db_invariant(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    first = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "conflict-1", "body": "original"},
        headers=admin.headers,
    )
    assert first.status_code == 201

    second = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "conflict-1", "body": "different"},
        headers=admin.headers,
    )
    assert second.status_code == 409

    row = (
        await db.execute(
            text(
                "SELECT count(*), max(body) FILTER (WHERE body = 'original') FROM wagle_messages "
                "WHERE room_id = :rid AND client_message_id = 'conflict-1'"
            ),
            {"rid": room_id},
        )
    ).one()
    assert row[0] == 1
    assert row[1] == "original"


# ---------------------------------------------------------------------------
# 6. read-state concurrent update -> monotonic non-regression
# ---------------------------------------------------------------------------

async def test_06_read_state_concurrent_update_monotonic(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    for i in range(10):
        r = await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"client_message_id": f"rs-{i}", "body": f"m{i}"},
            headers=admin.headers,
        )
        assert r.status_code == 201

    attempted = [2, 9, 1, 5, 8, 3]

    def factory(seq):
        async def put():
            return await client.put(
                f"/api/families/{family_id}/wagle/rooms/{room_id}/read-state",
                json={"last_read_sequence": seq},
                headers=member.headers,
            )

        return put

    results = await run_concurrent([factory(s) for s in attempted])
    assert all(not isinstance(r, Exception) for r in results)
    assert all(r.status_code == 200 for r in results), [r.status_code for r in results]

    final = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/read-state",
        headers=member.headers,
    )
    assert final.status_code == 200
    assert final.json()["last_read_sequence"] == max(attempted)


# ---------------------------------------------------------------------------
# 7. TEXT body boundary 4000 / 4001
# ---------------------------------------------------------------------------

async def test_07_text_body_boundary_4000_ok_4001_rejected(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    ok = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "len-4000", "body": "a" * 4000},
        headers=admin.headers,
    )
    assert ok.status_code == 201, ok.text
    assert len(ok.json()["body"]) == 4000

    before = await _counts(db, "wagle_messages")
    rejected = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "len-4001", "body": "a" * 4001},
        headers=admin.headers,
    )
    assert rejected.status_code == 422
    after = await _counts(db, "wagle_messages")
    assert before == after


# ---------------------------------------------------------------------------
# 8. client_message_id boundary 64 / 65
# ---------------------------------------------------------------------------

async def test_08_client_message_id_boundary_64_ok_65_rejected(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    ok = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "c" * 64, "body": "ok"},
        headers=admin.headers,
    )
    assert ok.status_code == 201, ok.text

    before = await _counts(db, "wagle_messages")
    rejected = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "c" * 65, "body": "rejected"},
        headers=admin.headers,
    )
    assert rejected.status_code == 422
    after = await _counts(db, "wagle_messages")
    assert before == after


# ---------------------------------------------------------------------------
# 9. pagination default 50 / max 100 / 101 rejected
# ---------------------------------------------------------------------------

async def test_09_pagination_default_50_max_100_reject_101(family_env):
    client, family_id = family_env["client"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    for i in range(60):
        r = await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"client_message_id": f"page-{i}", "body": f"m{i}"},
            headers=admin.headers,
        )
        assert r.status_code == 201

    default_resp = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", headers=admin.headers
    )
    assert default_resp.status_code == 200
    default_body = default_resp.json()
    assert len(default_body["items"]) == 50
    assert default_body["cursor"]["has_more_before"] is True

    max_resp = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        params={"limit": 100},
        headers=admin.headers,
    )
    assert max_resp.status_code == 200
    max_body = max_resp.json()
    assert len(max_body["items"]) == 60
    assert max_body["cursor"]["has_more_before"] is False

    over_resp = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        params={"limit": 101},
        headers=admin.headers,
    )
    assert over_resp.status_code == 422


# ---------------------------------------------------------------------------
# 10. GROUP active participant cap 50 / 51
# ---------------------------------------------------------------------------

async def test_10_group_active_participant_cap_50_51(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "big group", "participant_membership_ids": [member.membership_id]},
        headers=admin.headers,
    )
    assert room_resp.status_code == 201, room_resp.text
    room_id = room_resp.json()["id"]

    filler_ids = [await create_bare_membership(db, family_id, f"filler-{i}") for i in range(48)]

    for mid in filler_ids:
        r = await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/participants",
            json={"family_membership_id": mid, "room_role": "member"},
            headers=admin.headers,
        )
        assert r.status_code == 201, r.text

    active_count = (
        await db.execute(
            text(
                "SELECT count(*) FROM wagle_participants WHERE room_id = :rid AND status = 'active'"
            ),
            {"rid": room_id},
        )
    ).scalar_one()
    assert active_count == 50

    one_more = await create_bare_membership(db, family_id, "filler-51")
    over = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants",
        json={"family_membership_id": one_more, "room_role": "member"},
        headers=admin.headers,
    )
    assert over.status_code == 422, over.text

    final_count = (
        await db.execute(
            text(
                "SELECT count(*) FROM wagle_participants WHERE room_id = :rid AND status = 'active'"
            ),
            {"rid": room_id},
        )
    ).scalar_one()
    assert final_count == 50


# ---------------------------------------------------------------------------
# 11. cursor pagination: no duplicates, no gaps across a large volume
# ---------------------------------------------------------------------------

async def test_11_cursor_pagination_no_duplicates_no_gaps(family_env):
    client, family_id = family_env["client"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    total = 240
    for i in range(total):
        r = await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"client_message_id": f"cur-{i}", "body": f"m{i}"},
            headers=admin.headers,
        )
        assert r.status_code == 201

    # Always walk forward from the very beginning with an explicit
    # after_sequence cursor. list_messages()'s default (cursor-less) branch
    # returns the *newest* page instead, which is a different traversal
    # direction and not what a "walk every page once" dedup/gap check wants.
    seen: list[int] = []
    after = 0
    while True:
        resp = await client.get(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            params={"limit": 100, "after_sequence": after},
            headers=admin.headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        page_sequences = [item["sequence"] for item in body["items"]]
        assert page_sequences == sorted(page_sequences)
        seen.extend(page_sequences)
        if not body["cursor"]["has_more_after"]:
            break
        after = body["cursor"]["newest_sequence"]

    assert len(seen) == len(set(seen)), "cursor pagination produced duplicates"
    assert sorted(seen) == list(range(1, total + 1)), "cursor pagination has gaps"


# ---------------------------------------------------------------------------
# 12. LEFT / REMOVED / subscription-read-only boundaries
# ---------------------------------------------------------------------------

async def test_12a_left_participant_visibility_capped_and_write_denied(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "left-test", "participant_membership_ids": [member.membership_id]},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    for i in range(3):
        r = await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"client_message_id": f"before-leave-{i}", "body": f"m{i}"},
            headers=admin.headers,
        )
        assert r.status_code == 201

    leave = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/leave", headers=member.headers
    )
    assert leave.status_code == 200
    assert leave.json()["status"] == "left"
    left_sequence = leave.json()["left_sequence"]

    for i in range(3):
        r = await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"client_message_id": f"after-leave-{i}", "body": f"m{i}"},
            headers=admin.headers,
        )
        assert r.status_code == 201

    visible = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        params={"limit": 100},
        headers=member.headers,
    )
    assert visible.status_code == 200
    seqs = [item["sequence"] for item in visible.json()["items"]]
    assert all(s <= left_sequence for s in seqs)

    write_after_leave = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "should-fail", "body": "cannot"},
        headers=member.headers,
    )
    assert write_after_leave.status_code == 403


async def test_12b_removed_participant_denied(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "removed-test", "participant_membership_ids": [member.membership_id]},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    participants = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants", headers=admin.headers
    )
    member_participant_id = next(
        p["id"] for p in participants.json() if p["family_membership_id"] == member.membership_id
    )

    remove = await client.delete(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants/{member_participant_id}",
        headers=admin.headers,
    )
    assert remove.status_code == 200
    assert remove.json()["status"] == "removed"

    denied = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", headers=member.headers
    )
    assert denied.status_code == 403


async def test_12c_subscription_read_only_allows_read_denies_write(family_env):
    client, db, family_id = family_env["client"], family_env["db"], family_env["family_id"]
    admin, member = family_env["admin"], family_env["member"]

    room_resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": member.membership_id},
        headers=admin.headers,
    )
    room_id = room_resp.json()["id"]

    sent = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "before-suspend", "body": "hi"},
        headers=admin.headers,
    )
    assert sent.status_code == 201

    await db.execute(
        text("UPDATE service_subscriptions SET status = 'suspended' WHERE family_group_id = :fid AND service_code = 'wagle'"),
        {"fid": family_id},
    )
    await db.commit()

    still_readable = await client.get(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", headers=member.headers
    )
    assert still_readable.status_code == 200
    assert len(still_readable.json()["items"]) == 1

    before = await _counts(db, "wagle_messages")
    write_denied = await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"client_message_id": "after-suspend", "body": "should not land"},
        headers=admin.headers,
    )
    assert write_denied.status_code == 403
    after = await _counts(db, "wagle_messages")
    assert before == after
