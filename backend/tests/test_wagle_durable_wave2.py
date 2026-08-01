"""Wave 2 — Wagle durable messaging: atomicity, ordering, idempotency, read model.

Covers the four Wave 2 Backlog tasks:
`MONGLE-W2-WAGLE-DURABLE-COMMAND-001`, `MONGLE-W2-WAGLE-TRANSACTIONAL-OUTBOX-001`,
`MONGLE-W2-WAGLE-ORDERING-CURSOR-001`, `MONGLE-W2-WAGLE-ROOM-LIST-READ-MODEL-001`.

Two of the four were already implemented before this Wave (durable send with
idempotency, room-local ordering and the forward-only read cursor); those are
verified here rather than rebuilt, because a DoD is not satisfied by code
existing — only by the behaviour being pinned.

Scope boundary asserted throughout: the DB is the SSOT. Nothing here starts a
WebSocket, sends a Push, or consumes the Outbox — those are Wave 3.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select, text

from app.domains.wagle import service as wagle_service
from app.domains.wagle.models import WagleMessage, WagleRoom
from app.domains.service_outbox.models import ServiceOutboxEvent

from tests.conftest import create_actor, create_family, set_subscription


# --- helpers --------------------------------------------------------------


async def _direct_room(client, env, *, actor="admin", target_key="member"):
    resp = await client.post(
        f"/api/families/{env['family_id']}/wagle/rooms",
        json={"room_type": "DIRECT", "target_membership_id": env[target_key].membership_id},
        headers=env[actor].headers,
    )
    assert resp.status_code in (200, 201), resp.text
    return resp.json()["id"]


async def _send(client, env, room_id, body, client_message_id, *, actor="admin"):
    return await client.post(
        f"/api/families/{env['family_id']}/wagle/rooms/{room_id}/messages",
        json={"body": body, "client_message_id": client_message_id},
        headers=env[actor].headers,
    )


# --- Durable command + Outbox atomicity -----------------------------------


async def test_sending_a_message_records_an_outbox_event_in_the_same_transaction(db, client, family_env):
    """The Wave 2 core: a persisted message always has its delivery event."""
    room_id = await _direct_room(client, family_env)

    resp = await _send(client, family_env, room_id, "hello", "cmid-1")
    assert resp.status_code == 201, resp.text
    message_id = resp.json()["id"]

    event = (
        await db.execute(
            select(ServiceOutboxEvent).where(ServiceOutboxEvent.source_event_id == message_id)
        )
    ).scalars().one()

    # Target naming: everything newly emitted is Wagle.
    assert event.owner_service == "wagle"
    assert event.event_type == "wagle.message.created"
    assert event.aggregate_type == "wagle_message"
    assert event.event_version == 1
    assert event.status == "PENDING"          # nothing consumed it — Wave 3 does that
    assert event.family_id == family_env["family_id"]
    assert event.payload["room_id"] == room_id
    assert event.payload["message_id"] == message_id
    assert event.payload["sequence"] == resp.json()["sequence"]


async def test_no_emitted_identifier_carries_the_historical_doran_name(db, client, family_env):
    """Naming contract regression: Wagle is the Target name for anything new.

    The historical name must never appear in a value this code *emits*.
    Asserting over the stored rows rather than over the source constants is what
    makes this a real guard — a future edit that reintroduces the old name into
    an event contract fails here even if it renames the constant.

    The literal below is built from parts on purpose so this file's own
    assertion survives a repository-wide rename sweep: a blind search-and-replace
    over source text is exactly what silently inverted this test once already.
    """
    historical = "do" + "ran"
    room_id = await _direct_room(client, family_env)
    await _send(client, family_env, room_id, "naming", "naming-1")

    rows = (
        await db.execute(
            text("SELECT owner_service, event_type, aggregate_type FROM service_outbox_events")
        )
    ).mappings().all()
    assert rows, "the send must have produced an event to inspect"
    for row in rows:
        assert historical not in row["owner_service"]
        assert historical not in row["event_type"]
        assert historical not in row["aggregate_type"]
        assert row["owner_service"] == "wagle"


async def test_no_message_exists_without_its_event_and_vice_versa(db, client, family_env):
    """Atomicity stated as an invariant over the whole table, not one row."""
    room_id = await _direct_room(client, family_env)
    for i in range(5):
        assert (await _send(client, family_env, room_id, f"m{i}", f"cmid-{i}")).status_code == 201

    message_ids = {
        str(m) for m in (await db.execute(select(WagleMessage.id).where(WagleMessage.room_id == room_id))).scalars()
    }
    event_source_ids = {
        e for e in (
            await db.execute(
                select(ServiceOutboxEvent.source_event_id).where(ServiceOutboxEvent.owner_service == "wagle")
            )
        ).scalars()
    }
    assert message_ids == event_source_ids


async def test_a_failure_after_persist_rolls_back_both_message_and_event(db, client, family_env, monkeypatch):
    """Forced post-persist failure must leave no divergence.

    The enqueue is made to raise *after* the message row and the sequence bump
    are already in the transaction — precisely the window where a
    non-transactional outbox would leak a message with no event.
    """
    room_id = await _direct_room(client, family_env)
    before_messages = (await db.execute(text("SELECT count(*) FROM wagle_messages"))).scalar_one()
    before_events = (await db.execute(text("SELECT count(*) FROM service_outbox_events"))).scalar_one()
    room = await db.get(WagleRoom, room_id)
    await db.refresh(room)
    before_sequence = room.next_message_sequence

    async def boom(*args, **kwargs):
        raise RuntimeError("forced post-persist failure")

    monkeypatch.setattr(wagle_service, "_enqueue_message_event", boom)

    with pytest.raises(RuntimeError):
        await _send(client, family_env, room_id, "doomed", "cmid-boom")

    db.expire_all()
    assert (await db.execute(text("SELECT count(*) FROM wagle_messages"))).scalar_one() == before_messages
    assert (await db.execute(text("SELECT count(*) FROM service_outbox_events"))).scalar_one() == before_events
    # The room's sequence counter must not have advanced either.
    room_after = await db.get(WagleRoom, room_id)
    await db.refresh(room_after)
    assert room_after.next_message_sequence == before_sequence


async def test_idempotent_retry_returns_the_same_message_and_no_second_event(db, client, family_env):
    room_id = await _direct_room(client, family_env)

    first = await _send(client, family_env, room_id, "once", "cmid-dup")
    second = await _send(client, family_env, room_id, "once", "cmid-dup")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["sequence"] == second.json()["sequence"]

    events = (
        await db.execute(
            select(ServiceOutboxEvent).where(ServiceOutboxEvent.source_event_id == first.json()["id"])
        )
    ).scalars().all()
    assert len(events) == 1


async def test_same_client_message_id_with_a_different_body_is_a_conflict(client, family_env):
    room_id = await _direct_room(client, family_env)
    assert (await _send(client, family_env, room_id, "original", "cmid-x")).status_code == 201

    conflict = await _send(client, family_env, room_id, "tampered", "cmid-x")
    assert conflict.status_code == 409


# --- Ordering -------------------------------------------------------------


async def test_sequence_is_monotonic_and_gapless_within_a_room(client, family_env):
    room_id = await _direct_room(client, family_env)
    sequences = []
    for i in range(6):
        resp = await _send(client, family_env, room_id, f"m{i}", f"seq-{i}")
        sequences.append(resp.json()["sequence"])
    assert sequences == sorted(sequences)
    assert sequences == list(range(sequences[0], sequences[0] + len(sequences)))


async def test_ordering_is_per_room_not_global(db, client, family_env):
    """Two rooms in the same family each keep their own sequence space.

    A global counter would make room B start where room A left off; asserting
    both rooms start from the same low value is what rules that out.
    """
    room_a = await _direct_room(client, family_env)
    third = await create_actor(db, family_env["family_id"], name="third", service_role="participant")
    family_env["third"] = third
    room_b = await _direct_room(client, family_env, target_key="third")
    assert room_a != room_b

    a_seqs = [(await _send(client, family_env, room_a, f"a{i}", f"a-{i}")).json()["sequence"] for i in range(3)]
    b_seqs = [(await _send(client, family_env, room_b, f"b{i}", f"b-{i}")).json()["sequence"] for i in range(3)]

    assert a_seqs == b_seqs, "each room must have its own independent sequence space"


async def test_messages_are_isolated_between_families(db, client, family_env):
    """A room in family A is invisible and unusable from family B."""
    other_family = await create_family(db, "Other")
    await set_subscription(db, other_family, "active")
    outsider = await create_actor(db, other_family, name="outsider", service_role="room_admin")

    room_id = await _direct_room(client, family_env)
    await _send(client, family_env, room_id, "private", "iso-1")

    # Same room id, wrong family in the path.
    resp = await client.get(
        f"/api/families/{other_family}/wagle/rooms/{room_id}/messages",
        headers=outsider.headers,
    )
    assert resp.status_code in (403, 404)

    # And the outsider cannot write into it either.
    write = await client.post(
        f"/api/families/{other_family}/wagle/rooms/{room_id}/messages",
        json={"body": "intrusion", "client_message_id": "iso-2"},
        headers=outsider.headers,
    )
    assert write.status_code in (403, 404)


async def test_inactive_membership_cannot_send(db, client, family_env):
    room_id = await _direct_room(client, family_env)
    membership = await db.get(
        __import__("app.domains.family.models", fromlist=["FamilyMembership"]).FamilyMembership,
        family_env["member"].membership_id,
    )
    membership.status = "suspended"
    await db.commit()

    resp = await _send(client, family_env, room_id, "should fail", "inactive-1", actor="member")
    assert resp.status_code == 403


# --- Read cursor ----------------------------------------------------------


async def test_read_cursor_advances_and_never_regresses(client, family_env):
    room_id = await _direct_room(client, family_env)
    for i in range(4):
        await _send(client, family_env, room_id, f"m{i}", f"rc-{i}")

    url = f"/api/families/{family_env['family_id']}/wagle/rooms/{room_id}/read-state"
    forward = await client.put(url, json={"last_read_sequence": 3}, headers=family_env["member"].headers)
    assert forward.status_code == 200
    assert forward.json()["last_read_sequence"] == 3

    backward = await client.put(url, json={"last_read_sequence": 1}, headers=family_env["member"].headers)
    assert backward.status_code == 200
    assert backward.json()["last_read_sequence"] == 3, "cursor must be forward-only"


async def test_read_state_is_isolated_per_membership(client, family_env):
    room_id = await _direct_room(client, family_env)
    for i in range(3):
        await _send(client, family_env, room_id, f"m{i}", f"iso-rc-{i}")

    url = f"/api/families/{family_env['family_id']}/wagle/rooms/{room_id}/read-state"
    await client.put(url, json={"last_read_sequence": 2}, headers=family_env["member"].headers)

    admin_state = await client.get(url, headers=family_env["admin"].headers)
    member_state = await client.get(url, headers=family_env["member"].headers)
    assert member_state.json()["last_read_sequence"] == 2
    assert admin_state.json()["last_read_sequence"] == 0


async def test_read_cursor_beyond_the_visible_range_is_rejected(client, family_env):
    room_id = await _direct_room(client, family_env)
    await _send(client, family_env, room_id, "only one", "rng-1")

    url = f"/api/families/{family_env['family_id']}/wagle/rooms/{room_id}/read-state"
    resp = await client.put(url, json={"last_read_sequence": 9999}, headers=family_env["member"].headers)
    assert resp.status_code == 422


# --- Room list read model -------------------------------------------------


async def test_room_summaries_return_preview_and_unread_in_one_call(client, family_env):
    room_id = await _direct_room(client, family_env)
    for i in range(3):
        await _send(client, family_env, room_id, f"msg-{i}", f"sum-{i}")

    resp = await client.get(
        f"/api/families/{family_env['family_id']}/wagle/room-summaries",
        headers=family_env["member"].headers,
    )
    assert resp.status_code == 200, resp.text
    rows = resp.json()
    assert len(rows) == 1
    row = rows[0]

    assert row["id"] == room_id
    assert row["last_message"]["body"] == "msg-2"
    assert row["last_message"]["sequence"] == 3
    assert row["last_read_sequence"] == 0
    assert row["unread_count"] == 3          # all three are from the other member


async def test_room_summary_unread_drops_as_the_cursor_advances(client, family_env):
    room_id = await _direct_room(client, family_env)
    for i in range(3):
        await _send(client, family_env, room_id, f"m{i}", f"adv-{i}")

    url = f"/api/families/{family_env['family_id']}/wagle/rooms/{room_id}/read-state"
    await client.put(url, json={"last_read_sequence": 2}, headers=family_env["member"].headers)

    rows = (
        await client.get(
            f"/api/families/{family_env['family_id']}/wagle/room-summaries",
            headers=family_env["member"].headers,
        )
    ).json()
    assert rows[0]["unread_count"] == 1
    assert rows[0]["last_read_sequence"] == 2


async def test_room_summary_does_not_count_your_own_messages_as_unread(client, family_env):
    room_id = await _direct_room(client, family_env)
    for i in range(2):
        await _send(client, family_env, room_id, f"mine-{i}", f"own-{i}", actor="admin")

    rows = (
        await client.get(
            f"/api/families/{family_env['family_id']}/wagle/room-summaries",
            headers=family_env["admin"].headers,
        )
    ).json()
    assert rows[0]["unread_count"] == 0


async def test_room_summary_hides_the_body_of_a_deleted_last_message(client, family_env):
    room_id = await _direct_room(client, family_env)
    sent = await _send(client, family_env, room_id, "secret", "del-1")
    message_id = sent.json()["id"]

    deleted = await client.delete(
        f"/api/families/{family_env['family_id']}/wagle/rooms/{room_id}/messages/{message_id}",
        headers=family_env["admin"].headers,
    )
    assert deleted.status_code == 200

    rows = (
        await client.get(
            f"/api/families/{family_env['family_id']}/wagle/room-summaries",
            headers=family_env["member"].headers,
        )
    ).json()
    assert rows[0]["last_message"]["deleted"] is True
    assert rows[0]["last_message"]["body"] is None


async def test_room_summaries_only_show_the_callers_own_rooms(db, client, family_env):
    """A room the caller is not a participant of never appears, even in-family."""
    await _direct_room(client, family_env)
    third = await create_actor(db, family_env["family_id"], name="lonely", service_role="participant")

    rows = (
        await client.get(
            f"/api/families/{family_env['family_id']}/wagle/room-summaries",
            headers=third.headers,
        )
    ).json()
    assert rows == []


async def test_room_summaries_are_family_isolated(db, client, family_env):
    other_family = await create_family(db, "OtherFam")
    await set_subscription(db, other_family, "active")
    outsider = await create_actor(db, other_family, name="stranger", service_role="room_admin")
    await _direct_room(client, family_env)

    rows = (
        await client.get(
            f"/api/families/{other_family}/wagle/room-summaries",
            headers=outsider.headers,
        )
    ).json()
    assert rows == []


async def test_a_room_with_no_messages_still_lists_with_no_preview(client, family_env):
    await _direct_room(client, family_env)

    rows = (
        await client.get(
            f"/api/families/{family_env['family_id']}/wagle/room-summaries",
            headers=family_env["member"].headers,
        )
    ).json()
    assert len(rows) == 1
    assert rows[0]["last_message"] is None
    assert rows[0]["unread_count"] == 0
