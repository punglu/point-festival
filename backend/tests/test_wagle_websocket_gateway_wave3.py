"""Wave 3: the WebSocket gateway handler, driven end to end.

**What this covers and what it does not.** These tests await the real
`wagle_realtime_socket` coroutine — the same authentication, the same
subscribe/resume/unsubscribe loop, the same background revalidation, the same
registry — against a scripted socket object. Only the network framing is
stubbed.

Framing is stubbed rather than driven through `TestClient` for a concrete
reason, not convenience: `TestClient` runs the app in its own thread and event
loop, while the async engine and its asyncpg connections are bound to the
test's loop. Sharing them across loops fails in ways that look like product
bugs. Real browser framing is covered by the Playwright suite instead, and this
file does not claim to cover it.
"""
from __future__ import annotations

import asyncio
import uuid

import pytest
from sqlalchemy import select, update

from app.domains.family import auth_service
from app.domains.family.models import Account, AccountSession, FamilyMembership
from app.domains.wagle import realtime
from app.domains.wagle.realtime_router import wagle_realtime_socket
from tests.conftest import create_actor, create_family


class ScriptedWebSocket:
    """A WebSocket the test drives. Records everything the server sends."""

    def __init__(self, inbound: list[dict], *, hold_open: bool = False):
        self._inbound = list(inbound)
        self.sent: list[dict] = []
        self.accepted = False
        self.closed_with: int | None = None
        # When the script runs out, a real client is still connected and simply
        # quiet. `hold_open=True` models that. Without it the handler sees an
        # immediate disconnect and unregisters the connection in its `finally`
        # block - which is correct behaviour, and made an earlier draft of the
        # fan-out test publish to an already-closed connection and assert 0.
        self._hold_open = hold_open
        self._release = asyncio.Event()

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, payload: dict) -> None:
        self.sent.append(payload)

    async def receive_json(self):
        if self._inbound:
            return self._inbound.pop(0)
        from fastapi import WebSocketDisconnect

        if self._hold_open:
            # Stay connected and idle until the test is done observing.
            await self._release.wait()
        raise WebSocketDisconnect(code=1000)

    def release(self) -> None:
        """Let a held-open socket finish, exercising the handler's cleanup."""
        self._release.set()

    async def close(self, code: int = 1000) -> None:
        self.closed_with = code

    def types(self) -> list[str]:
        return [m.get("type") for m in self.sent]

    def first(self, message_type: str) -> dict | None:
        return next((m for m in self.sent if m.get("type") == message_type), None)

    def all_of(self, message_type: str) -> list[dict]:
        return [m for m in self.sent if m.get("type") == message_type]


async def _run_socket(socket: ScriptedWebSocket, token: str | None) -> None:
    await wagle_realtime_socket(socket, token=token)


async def _login(db, client, display_name: str, username: str, device_id: str = "dev-ws"):
    account = (
        await db.execute(select(Account).where(Account.display_name == display_name))
    ).scalars().first()
    await auth_service.create_credential(db, account.id, username, "Str0ngPassw0rd!")
    await db.commit()
    resp = await client.post(
        "/api/auth/account/login",
        json={"username": username, "password": "Str0ngPassw0rd!", "device_id": device_id},
    )
    assert resp.status_code == 200, resp.text
    return account, resp.json()["access_token"]


async def _room_with_both_actors(env, *, body: str | None = "hello"):
    client, family_id = env["client"], env["family_id"]
    room = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "ws"},
        headers=env["admin"].headers,
    )
    room_id = room.json()["id"]
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants",
        json={"family_membership_id": env["member"].membership_id, "room_role": "member"},
        headers=env["admin"].headers,
    )
    if body is not None:
        await client.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"body": body, "client_message_id": str(uuid.uuid4())},
            headers=env["admin"].headers,
        )
    return room_id


# ===========================================================================
# Authentication
# ===========================================================================


async def test_socket_without_a_token_is_refused():
    socket = ScriptedWebSocket([])
    await _run_socket(socket, token=None)
    assert socket.accepted is True
    assert socket.first("error")["code"] == "unauthorized"
    assert socket.closed_with == 4401
    assert socket.first("connected") is None


async def test_socket_rejects_a_legacy_player_token(family_env):
    """A legacy MarkPoint player JWT must not open an Account-native channel."""
    from tests.conftest import make_token

    socket = ScriptedWebSocket([])
    await _run_socket(socket, token=make_token(family_env["member"].player_id))
    assert socket.first("error")["code"] == "unauthorized"
    assert socket.closed_with == 4401


async def test_socket_rejects_a_revoked_session(family_env, db, client):
    account, token = await _login(db, client, "member", "member.revoked")
    session_row = (
        await db.execute(
            select(AccountSession).where(AccountSession.account_id == account.id)
        )
    ).scalars().first()
    await auth_service.logout(db, session_row.id)

    socket = ScriptedWebSocket([])
    await _run_socket(socket, token=token)
    assert socket.first("error")["code"] == "unauthorized", (
        "a revoked Session must stop working immediately, not when the access token expires"
    )


async def test_socket_rejects_a_suspended_account(family_env, db, client):
    account, token = await _login(db, client, "member", "member.susp")
    await db.execute(update(Account).where(Account.id == account.id).values(status="suspended"))
    await db.commit()

    socket = ScriptedWebSocket([])
    await _run_socket(socket, token=token)
    assert socket.first("error")["code"] == "unauthorized"


async def test_connected_frame_carries_the_server_derived_family_set(family_env, db, client):
    account, token = await _login(db, client, "member", "member.hello")
    socket = ScriptedWebSocket([])
    await _run_socket(socket, token=token)

    connected = socket.first("connected")
    assert connected is not None
    assert connected["account_id"] == account.id
    assert connected["authorized_family_ids"] == [family_env["family_id"]]
    assert "connection_id" in connected


# ===========================================================================
# Subscription
# ===========================================================================


async def test_subscribe_then_receive_a_fanned_out_event(family_env, db, client):
    """The delivery path a connected client actually depends on."""
    family_id = family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body=None)
    _, token = await _login(db, client, "member", "member.sub")

    socket = ScriptedWebSocket(
        [{"action": "subscribe", "family_id": family_id, "room_id": room_id}], hold_open=True
    )
    task = asyncio.create_task(_run_socket(socket, token=token))
    for _ in range(50):
        await asyncio.sleep(0.01)
        if socket.first("subscribed"):
            break
    assert socket.first("subscribed") is not None, socket.sent

    envelope = realtime.RealtimeEnvelope(
        "e1", "wagle.message.created", family_id, room_id, "m1", 1, "2026-08-01T00:00:00+00:00", "ACCOUNT"
    )
    delivered = await realtime.fanout.publish(envelope)
    assert delivered == 1

    events = socket.all_of("event")
    assert len(events) == 1
    assert events[0]["room_sequence"] == 1
    # Identifiers only: the transport is not allowed to be a second copy of the
    # message, and D6-P1 has not decided any disclosure level.
    assert "body" not in events[0] and "text" not in events[0]

    socket.release()
    await asyncio.wait_for(task, timeout=5)


async def test_subscribe_is_denied_for_a_room_in_another_family_without_closing_the_socket(
    family_env, db, client
):
    family_id = family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body=None)

    other_family = await create_family(db, "Neighbour")
    outsider = await create_actor(db, other_family, name="ws-outsider")
    await db.commit()
    _, token = await _login(db, client, "ws-outsider", "wsoutsider.u", "dev-out")

    socket = ScriptedWebSocket(
        [
            {"action": "subscribe", "family_id": family_id, "room_id": room_id},
            {"action": "ping"},
        ]
    )
    await _run_socket(socket, token=token)

    assert socket.first("subscribe_denied") is not None
    assert socket.first("subscribed") is None
    # One denial must not kill the connection — a client with several families
    # and one stale room should keep the rest working.
    assert socket.first("pong") is not None


async def test_client_supplied_family_id_is_not_trusted(family_env, db, client):
    """The client asks; the server re-derives. `activeFamilyId` is never input
    to an authorization decision."""
    room_id = await _room_with_both_actors(family_env, body=None)
    _, token = await _login(db, client, "member", "member.spoof")

    socket = ScriptedWebSocket(
        [{"action": "subscribe", "family_id": 99999, "room_id": room_id}]
    )
    await _run_socket(socket, token=token)
    assert socket.first("subscribe_denied") is not None
    assert socket.first("subscribed") is None


async def test_unsubscribe_stops_delivery(family_env, db, client):
    family_id = family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body=None)
    _, token = await _login(db, client, "member", "member.unsub")

    socket = ScriptedWebSocket(
        [
            {"action": "subscribe", "family_id": family_id, "room_id": room_id},
            {"action": "unsubscribe", "family_id": family_id, "room_id": room_id},
        ]
    )
    await _run_socket(socket, token=token)
    assert socket.first("unsubscribed") is not None

    envelope = realtime.RealtimeEnvelope(
        "e", "wagle.message.created", family_id, room_id, "m", 1, "t", "ACCOUNT"
    )
    assert await realtime.fanout.publish(envelope) == 0


async def test_two_sockets_on_one_session_are_both_served(family_env, db, client):
    """Multiple physical sockets per Session are legitimate — the Realtime
    Messaging Contract forbids an invariant that treats them as an error."""
    family_id = family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body=None)
    _, token = await _login(db, client, "member", "member.tabs")

    sockets = [
        ScriptedWebSocket(
            [{"action": "subscribe", "family_id": family_id, "room_id": room_id}], hold_open=True
        )
        for _ in range(2)
    ]
    tasks = [asyncio.create_task(_run_socket(s, token=token)) for s in sockets]
    for _ in range(50):
        await asyncio.sleep(0.01)
        if all(s.first("subscribed") for s in sockets):
            break
    assert all(s.first("subscribed") for s in sockets), [s.sent for s in sockets]

    envelope = realtime.RealtimeEnvelope(
        "e", "wagle.message.created", family_id, room_id, "m", 1, "t", "ACCOUNT"
    )
    assert await realtime.fanout.publish(envelope) == 2
    assert all(len(s.all_of("event")) == 1 for s in sockets)

    for s in sockets:
        s.release()
    await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)


async def test_one_socket_can_hold_subscriptions_in_several_families(family_env, db, client):
    """One logical subscription spans the whole AuthorizedFamilySet (D1)."""
    from datetime import datetime, timezone

    from app.domains.wagle.models import WagleParticipant, WagleRoom

    family_id = family_env["family_id"]
    room_a = await _room_with_both_actors(family_env, body=None)
    account = await db.get(Account, family_env["member"].account_id)

    family_b = await create_family(db, "Second")
    membership_b = FamilyMembership(
        family_group_id=family_b,
        account_id=account.id,
        relationship="unknown",
        status="active",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership_b)
    await db.flush()
    room = WagleRoom(
        family_group_id=family_b,
        room_type="GROUP",
        title="b",
        status="active",
        created_by_actor_type="ACCOUNT",
        next_message_sequence=0,
    )
    db.add(room)
    await db.flush()
    db.add(
        WagleParticipant(
            family_group_id=family_b,
            room_id=room.id,
            family_membership_id=membership_b.id,
            room_role="member",
            status="active",
            joined_sequence=0,
        )
    )
    await db.commit()
    room_b = str(room.id)

    _, token = await _login(db, client, "member", "member.multi")
    socket = ScriptedWebSocket(
        [
            {"action": "subscribe", "family_id": family_id, "room_id": room_a},
            {"action": "subscribe", "family_id": family_b, "room_id": room_b},
        ],
        hold_open=True,
    )
    task = asyncio.create_task(_run_socket(socket, token=token))
    for _ in range(60):
        await asyncio.sleep(0.01)
        if len(socket.all_of("subscribed")) == 2:
            break
    assert len(socket.all_of("subscribed")) == 2, socket.sent

    assert await realtime.fanout.publish(
        realtime.RealtimeEnvelope("e1", "t", family_id, room_a, "m", 1, "t", "ACCOUNT")
    ) == 1
    assert await realtime.fanout.publish(
        realtime.RealtimeEnvelope("e2", "t", family_b, room_b, "m", 1, "t", "ACCOUNT")
    ) == 1
    assert len(socket.all_of("event")) == 2

    socket.release()
    await asyncio.wait_for(task, timeout=5)


# ===========================================================================
# Resume over the socket
# ===========================================================================


async def test_resume_over_the_socket_returns_missed_messages_in_order(family_env, db, client):
    client_, family_id = family_env["client"], family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body="first")
    for body in ("second", "third"):
        await client_.post(
            f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
            json={"body": body, "client_message_id": str(uuid.uuid4())},
            headers=family_env["admin"].headers,
        )
    _, token = await _login(db, client, "member", "member.resume")

    socket = ScriptedWebSocket(
        [{"action": "resume", "family_id": family_id, "room_id": room_id, "after_sequence": 0}]
    )
    await _run_socket(socket, token=token)

    resume = socket.first("resume")
    assert resume is not None, socket.sent
    sequences = [e["room_sequence"] for e in resume["events"]]
    assert sequences == sorted(sequences) and len(sequences) == 3


async def test_resume_is_denied_for_an_unauthorized_room(family_env, db, client):
    family_id = family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body="x")
    other_family = await create_family(db, "Far")
    await create_actor(db, other_family, name="ws-far")
    await db.commit()
    _, token = await _login(db, client, "ws-far", "wsfar.u", "dev-far")

    socket = ScriptedWebSocket(
        [{"action": "resume", "family_id": family_id, "room_id": room_id, "after_sequence": 0}]
    )
    await _run_socket(socket, token=token)
    assert socket.first("resume_denied") is not None
    assert socket.first("resume") is None


async def test_unknown_action_is_reported_without_closing_the_socket(family_env, db, client):
    _, token = await _login(db, client, "member", "member.unknown")
    socket = ScriptedWebSocket([{"action": "nonsense"}, {"action": "ping"}])
    await _run_socket(socket, token=token)
    assert socket.first("error")["code"] == "unknown_action"
    assert socket.first("pong") is not None


# ===========================================================================
# Cleanup
# ===========================================================================


async def test_disconnect_unregisters_the_connection(family_env, db, client):
    family_id = family_env["family_id"]
    room_id = await _room_with_both_actors(family_env, body=None)
    _, token = await _login(db, client, "member", "member.cleanup")

    socket = ScriptedWebSocket([{"action": "subscribe", "family_id": family_id, "room_id": room_id}])
    await _run_socket(socket, token=token)

    # The script ran out, which the handler sees as a disconnect. Nothing may
    # be left in the registry, or a dead socket keeps receiving fan-out.
    envelope = realtime.RealtimeEnvelope(
        "e", "wagle.message.created", family_id, room_id, "m", 1, "t", "ACCOUNT"
    )
    assert await realtime.fanout.publish(envelope) == 0
