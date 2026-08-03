"""W7.5 Phase D — SLICE-WAGLE-BOARD-REACTIONS (3e, 인기 게시글).

Resolved as IMPLEMENTATION_REQUIRED, not a PM policy gate: the reaction
concept (a single heart icon, no reaction-type picker) is already fully
determined by the frozen `3c`/`3e` canonical Screens themselves, which
already render `♥ {likes} · 💬 {comments}` as a core visual element. See
`backend/alembic/versions/0020_wagle_message_reactions.py`'s own docstring.

Every fixture here is synthetic, created inside the isolated Phase 2 test
database.
"""
from __future__ import annotations

import pytest


async def _create_board_room(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    from app.domains.wagle.board_constants import FAMILY_BOARD_ROOM_TITLE
    resp = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": FAMILY_BOARD_ROOM_TITLE, "participant_membership_ids": [member.membership_id]},
        headers=admin.headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _post_message(family_env, room_id, body, headers, client_message_id, reply_to=None):
    client, family_id = family_env["client"], family_env["family_id"]
    payload = {"client_message_id": client_message_id, "body": body}
    if reply_to is not None:
        payload["reply_to_message_id"] = reply_to
    resp = await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_reaction_toggle_on_then_off(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "이번 주말 나들이", admin.headers, "p1")

    first = await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=member.headers)
    assert first.status_code == 200, first.text
    assert first.json()["reacted_by_me"] is True
    assert first.json()["reaction_count"] == 1

    second = await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=member.headers)
    assert second.status_code == 200
    assert second.json()["reacted_by_me"] is False
    assert second.json()["reaction_count"] == 0


@pytest.mark.asyncio
async def test_reaction_count_is_per_message_and_multi_actor(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "여름 여행", admin.headers, "p2")

    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=admin.headers)
    resp = await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=member.headers)
    assert resp.json()["reaction_count"] == 2


@pytest.mark.asyncio
async def test_message_list_includes_real_reaction_count_and_viewer_state(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "댓글 테스트", admin.headers, "p3")
    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=member.headers)

    as_member = await client.get(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", headers=member.headers)
    item = next(m for m in as_member.json()["items"] if m["id"] == post["id"])
    assert item["reaction_count"] == 1
    assert item["reacted_by_me"] is True

    as_admin = await client.get(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", headers=admin.headers)
    item2 = next(m for m in as_admin.json()["items"] if m["id"] == post["id"])
    assert item2["reaction_count"] == 1
    assert item2["reacted_by_me"] is False


@pytest.mark.asyncio
async def test_popular_posts_ranked_by_reactions_plus_comments(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    low = await _post_message(family_env, room_id, "인기 없는 글", admin.headers, "low")
    high = await _post_message(family_env, room_id, "인기 많은 글", admin.headers, "high")
    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{high['id']}/reactions", headers=admin.headers)
    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{high['id']}/reactions", headers=member.headers)
    await _post_message(family_env, room_id, "댓글", member.headers, "comment-1", reply_to=high["id"])

    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": "all"}, headers=admin.headers)
    assert resp.status_code == 200, resp.text
    ranked_ids = [p["message_id"] for p in resp.json()]
    assert ranked_ids[0] == high["id"]
    assert resp.json()[0]["reaction_count"] == 2
    assert resp.json()[0]["comment_count"] == 1
    assert low["id"] in ranked_ids


@pytest.mark.asyncio
async def test_popular_posts_excludes_replies_as_top_level_entries(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "원글", admin.headers, "orig")
    await _post_message(family_env, room_id, "댓글", member.headers, "reply1", reply_to=post["id"])

    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": "all"}, headers=admin.headers)
    ids = [p["message_id"] for p in resp.json()]
    assert post["id"] in ids
    reply_id = None
    listed = await client.get(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages", headers=admin.headers)
    for m in listed.json()["items"]:
        if m.get("reply_to_message_id") == post["id"]:
            reply_id = m["id"]
    assert reply_id is not None
    assert reply_id not in ids


@pytest.mark.asyncio
async def test_popular_posts_returns_empty_when_no_board_room_exists(family_env):
    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": "week"}, headers=admin.headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_reaction_requires_send_permission_and_participation(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "권한 테스트", admin.headers, "perm1")

    unauth = await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions")
    assert unauth.status_code == 401


@pytest.mark.asyncio
async def test_reaction_on_nonexistent_message_404s(family_env):
    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    room_id = await _create_board_room(family_env)
    import uuid
    fake_id = uuid.uuid4()
    resp = await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{fake_id}/reactions", headers=admin.headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# W7.5 Independent QA remediation (F1): `range=week`/`range=month` crashed
# with a real 500 (asyncpg.exceptions.DataError: invalid input for query
# argument $2: 30 (expected str, got int)) because `list_popular_posts`
# bound the days count as an integer parameter into
# `(:days || ' days')::interval` -- PostgreSQL's `||` has no integer/text
# overload. None of the tests above ever exercised this: they either pass
# `range="all"` (no interval binding at all -- `since_clause` stays empty)
# or hit the empty-board-room early return before the interval SQL ever
# runs. Fixed to `:days * INTERVAL '1 day'`, keeping `days` a genuine bound
# parameter. These tests exercise exactly the branch the bug lived in --
# a real board room, a real post, and `range="week"`/`"month"` specifically.
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_popular_posts_week_range_with_real_post_returns_200(family_env):
    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "이번 주 글", admin.headers, "week1")

    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": "week"}, headers=admin.headers)
    assert resp.status_code == 200, resp.text
    assert post["id"] in [p["message_id"] for p in resp.json()]


@pytest.mark.asyncio
async def test_popular_posts_month_range_with_real_post_returns_200(family_env):
    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "이번 달 글", admin.headers, "month1")

    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": "month"}, headers=admin.headers)
    assert resp.status_code == 200, resp.text
    assert post["id"] in [p["message_id"] for p in resp.json()]


@pytest.mark.asyncio
async def test_popular_posts_default_range_returns_200(family_env):
    """The router defaults `range` to `"week"` (`Query("week")`) -- calling
    the endpoint with no query param at all must hit the exact same
    previously-broken code path, not a different default."""
    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "기본 range 글", admin.headers, "default1")

    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", headers=admin.headers)
    assert resp.status_code == 200, resp.text
    assert post["id"] in [p["message_id"] for p in resp.json()]


@pytest.mark.asyncio
async def test_popular_posts_invalid_range_is_a_validation_error_not_500(family_env):
    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    await _create_board_room(family_env)

    resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": "bogus"}, headers=admin.headers)
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_popular_posts_week_and_month_exclude_posts_outside_the_window(family_env):
    """A post older than the window must not appear under `week`/`month`,
    but must still appear under `all` -- the exact date-arithmetic path the
    interval-binding bug lived in, now verified end to end rather than
    only checked for a non-crashing status code."""
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import text as sa_text

    client, family_id, admin, db = family_env["client"], family_env["family_id"], family_env["admin"], family_env["db"]
    room_id = await _create_board_room(family_env)
    recent = await _post_message(family_env, room_id, "최근 글", admin.headers, "recent1")
    old = await _post_message(family_env, room_id, "45일 전 글", admin.headers, "old1")

    # Backdate the second post 45 days -- past both the 7-day and 30-day
    # windows but still real inside `all`.
    await db.execute(
        sa_text("UPDATE wagle_messages SET created_at = :ts WHERE id = :id"),
        {"ts": datetime.now(timezone.utc) - timedelta(days=45), "id": old["id"]},
    )
    await db.commit()

    week_ids = [p["message_id"] for p in (await client.get(
        f"/api/families/{family_id}/wagle/board/popular", params={"range": "week"}, headers=admin.headers,
    )).json()]
    month_ids = [p["message_id"] for p in (await client.get(
        f"/api/families/{family_id}/wagle/board/popular", params={"range": "month"}, headers=admin.headers,
    )).json()]
    all_ids = [p["message_id"] for p in (await client.get(
        f"/api/families/{family_id}/wagle/board/popular", params={"range": "all"}, headers=admin.headers,
    )).json()]

    assert recent["id"] in week_ids and old["id"] not in week_ids
    assert recent["id"] in month_ids and old["id"] not in month_ids
    assert recent["id"] in all_ids and old["id"] in all_ids


@pytest.mark.asyncio
async def test_popular_posts_does_not_leak_across_families(family_env):
    """A board post in one Family must never appear in another Family's
    ranked Popular Posts, regardless of range."""
    from tests.conftest import create_family, create_actor, set_subscription

    client, family_id, admin = family_env["client"], family_env["family_id"], family_env["admin"]
    db = family_env["db"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "가족A 글", admin.headers, "familyA1")

    other_family_id = await create_family(db, name="Other Family")
    other_admin = await create_actor(db, other_family_id, name="other-admin", service_role="room_admin")
    await set_subscription(db, other_family_id, "active")

    resp = await client.get(
        f"/api/families/{other_family_id}/wagle/board/popular", params={"range": "all"}, headers=other_admin.headers,
    )
    assert resp.status_code == 200, resp.text
    assert post["id"] not in [p["message_id"] for p in resp.json()]


@pytest.mark.asyncio
async def test_popular_posts_reaction_and_comment_aggregation_is_accurate(family_env):
    client, family_id, admin, member = family_env["client"], family_env["family_id"], family_env["admin"], family_env["member"]
    room_id = await _create_board_room(family_env)
    post = await _post_message(family_env, room_id, "집계 정확성 테스트", admin.headers, "agg1")

    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=admin.headers)
    await client.post(f"/api/families/{family_id}/wagle/rooms/{room_id}/messages/{post['id']}/reactions", headers=member.headers)
    await _post_message(family_env, room_id, "댓글1", member.headers, "agg-comment-1", reply_to=post["id"])
    await _post_message(family_env, room_id, "댓글2", admin.headers, "agg-comment-2", reply_to=post["id"])

    for range_value in ("week", "month", "all"):
        resp = await client.get(f"/api/families/{family_id}/wagle/board/popular", params={"range": range_value}, headers=admin.headers)
        assert resp.status_code == 200, resp.text
        row = next(p for p in resp.json() if p["message_id"] == post["id"])
        assert row["reaction_count"] == 2, f"range={range_value}"
        assert row["comment_count"] == 2, f"range={range_value}"
