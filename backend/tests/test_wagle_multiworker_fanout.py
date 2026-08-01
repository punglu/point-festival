"""MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001: cross-worker realtime delivery.

**What "two workers" means here.** Each `PostgresNotifyFanout` opens its own
dedicated asyncpg connection and its own registry, exactly as a separate ASGI
worker does. Two of them in one test process are two independent
listener/registry pairs talking through a real PostgreSQL NOTIFY — the same
code path and the same database round trip that `uvicorn --workers 2` uses.
What a single process cannot reproduce is OS-level process isolation, so the
runtime `--workers 2` check is recorded separately in the task report rather
than claimed here.

The properties under test are the ones that make NOTIFY safe to depend on
*and* safe to lose:

- an event handled by worker A reaches a connection held by worker B,
- a duplicate notification does not produce a duplicate render,
- a **missed** notification is still recovered by the durable cursor, which is
  what keeps NOTIFY optional rather than load-bearing,
- a listener that dies reconnects and resumes receiving,
- and the payload never carries message content.
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid

import pytest

from app.domains.wagle.realtime import Connection, InProcessFanout, RealtimeEnvelope
from app.domains.wagle.realtime_notify import (
    CHANNEL,
    MAX_PAYLOAD_BYTES,
    PostgresNotifyFanout,
    to_asyncpg_dsn,
)

DSN = to_asyncpg_dsn(os.environ["DATABASE_URL"])


class RecordingSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def __call__(self, payload: dict) -> None:
        self.sent.append(payload)

    def events(self) -> list[dict]:
        return [m for m in self.sent if m.get("type") == "event"]


def envelope(family_id: int, room_id: str, sequence: int = 1) -> RealtimeEnvelope:
    return RealtimeEnvelope(
        event_id=str(uuid.uuid4()),
        event_type="wagle.message.created",
        family_id=family_id,
        room_id=room_id,
        message_id=str(uuid.uuid4()),
        room_sequence=sequence,
        occurred_at="2026-08-01T00:00:00+00:00",
        actor_type="ACCOUNT",
    )


async def _await_events(socket: RecordingSocket, count: int, timeout: float = 5.0) -> bool:
    """Wait for delivery instead of sleeping a fixed amount.

    A fixed sleep would either make the suite slow or make it flaky, and a
    flaky realtime test is worse than none — it trains the reader to re-run
    rather than to look.
    """
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        if len(socket.events()) >= count:
            return True
        await asyncio.sleep(0.05)
    return len(socket.events()) >= count


class TwoWorkers:
    """Two independent registry + listener pairs, torn down deterministically."""

    def __init__(self) -> None:
        self.local_a = InProcessFanout()
        self.local_b = InProcessFanout()
        self.a = PostgresNotifyFanout(self.local_a, DSN)
        self.b = PostgresNotifyFanout(self.local_b, DSN)

    async def __aenter__(self) -> "TwoWorkers":
        await self.a.start_listener()
        await self.b.start_listener()
        for _ in range(100):
            if self.a.is_listening and self.b.is_listening:
                break
            await asyncio.sleep(0.05)
        assert self.a.is_listening and self.b.is_listening, "listeners failed to attach"
        return self

    async def __aexit__(self, *_exc) -> None:
        await self.a.stop_listener()
        await self.b.stop_listener()


# ===========================================================================
# The required condition: A handles the event, B's client receives it
# ===========================================================================


async def test_event_handled_on_worker_a_reaches_a_connection_on_worker_b():
    room_id = str(uuid.uuid4())
    async with TwoWorkers() as workers:
        socket_b = RecordingSocket()
        await workers.local_b.register(Connection("b1", 1, 10, None, socket_b, {7: {room_id}}))

        # Worker A publishes. It has no local subscriber at all, so anything
        # `socket_b` receives arrived through PostgreSQL.
        delivered_locally = await workers.a.publish(envelope(7, room_id, 5))
        assert delivered_locally == 0

        assert await _await_events(socket_b, 1), socket_b.sent
        event = socket_b.events()[0]
        assert event["room_sequence"] == 5
        assert event["room_id"] == room_id


async def test_the_publishing_worker_does_not_deliver_the_same_event_twice():
    """`origin_id` stops a worker from re-delivering its own notification.

    Client dedup would mask this, but creating a duplicate the server knows
    about and leaving the client to clean it up is the wrong default.
    """
    room_id = str(uuid.uuid4())
    async with TwoWorkers() as workers:
        socket_a = RecordingSocket()
        await workers.local_a.register(Connection("a1", 1, 10, None, socket_a, {7: {room_id}}))

        delivered = await workers.a.publish(envelope(7, room_id, 3))
        assert delivered == 1
        await asyncio.sleep(1.0)  # long enough for its own NOTIFY to come back

        assert len(socket_a.events()) == 1, socket_a.sent
        assert workers.a.skipped_own >= 1


async def test_subscribers_in_other_families_or_rooms_are_not_woken():
    room_id, other_room = str(uuid.uuid4()), str(uuid.uuid4())
    async with TwoWorkers() as workers:
        target, wrong_room, wrong_family = RecordingSocket(), RecordingSocket(), RecordingSocket()
        await workers.local_b.register(Connection("b1", 1, 10, None, target, {7: {room_id}}))
        await workers.local_b.register(Connection("b2", 2, 20, None, wrong_room, {7: {other_room}}))
        await workers.local_b.register(Connection("b3", 3, 30, None, wrong_family, {8: {room_id}}))

        await workers.a.publish(envelope(7, room_id, 1))
        assert await _await_events(target, 1)
        await asyncio.sleep(0.3)

        assert wrong_room.events() == []
        assert wrong_family.events() == [], "same room id in another family must not match"


# ===========================================================================
# NOTIFY is optional: duplicates are safe, losses are recovered
# ===========================================================================


async def test_a_duplicate_notification_carries_the_same_identifiers_for_client_dedup():
    """The transport may repeat. That is safe only because every copy carries
    the same `(room_id, room_sequence)` and `message_id` the client dedupes on."""
    room_id = str(uuid.uuid4())
    async with TwoWorkers() as workers:
        socket_b = RecordingSocket()
        await workers.local_b.register(Connection("b1", 1, 10, None, socket_b, {7: {room_id}}))

        duplicated = envelope(7, room_id, 9)
        await workers.a.publish(duplicated)
        await workers.a.publish(duplicated)

        assert await _await_events(socket_b, 2), socket_b.sent
        events = socket_b.events()
        assert {e["message_id"] for e in events} == {duplicated.message_id}
        assert {e["room_sequence"] for e in events} == {9}


async def test_a_missed_notification_is_still_recoverable_from_the_durable_cursor(
    family_env, db, client
):
    """The fallback that makes NOTIFY optional.

    No NOTIFY is emitted at all here: the message is simply committed, and the
    durable resume query is asked what the client missed. If this ever stops
    working, losing a notification would start losing a message.
    """
    from app.domains.family.models import Account
    from app.domains.wagle import realtime

    family_id = family_env["family_id"]
    room = await client.post(
        f"/api/families/{family_id}/wagle/rooms",
        json={"room_type": "GROUP", "title": "missed"},
        headers=family_env["admin"].headers,
    )
    room_id = room.json()["id"]
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/participants",
        json={"family_membership_id": family_env["member"].membership_id, "room_role": "member"},
        headers=family_env["admin"].headers,
    )
    await client.post(
        f"/api/families/{family_id}/wagle/rooms/{room_id}/messages",
        json={"body": "arrived while the listener was down", "client_message_id": str(uuid.uuid4())},
        headers=family_env["admin"].headers,
    )

    account = await db.get(Account, family_env["member"].account_id)
    recovered = await realtime.resume_missed_events(db, account, family_id, room_id, 0)
    assert len(recovered["events"]) == 1
    assert recovered["events"][0]["event_type"] == "wagle.message.created"


# ===========================================================================
# Listener lifecycle
# ===========================================================================


async def test_a_listener_that_loses_its_connection_reconnects_and_resumes():
    room_id = str(uuid.uuid4())
    async with TwoWorkers() as workers:
        socket_b = RecordingSocket()
        await workers.local_b.register(Connection("b1", 1, 10, None, socket_b, {7: {room_id}}))

        await workers.a.publish(envelope(7, room_id, 1))
        assert await _await_events(socket_b, 1)

        # Kill B's listener connection the way a network blip or a database
        # restart would, rather than by calling stop().
        assert workers.b._listen_conn is not None
        await workers.b._listen_conn.close()

        for _ in range(200):
            if workers.b.is_listening:
                break
            await asyncio.sleep(0.05)
        assert workers.b.is_listening, "listener did not reconnect"

        await workers.a.publish(envelope(7, room_id, 2))
        assert await _await_events(socket_b, 2), socket_b.sent
        # Nothing is replayed on reconnect - the event missed while down is the
        # durable cursor's job, not the listener's.
        assert [e["room_sequence"] for e in socket_b.events()] == [1, 2]


async def test_stopping_the_listener_is_clean_and_idempotent():
    workers = TwoWorkers()
    await workers.a.start_listener()
    for _ in range(100):
        if workers.a.is_listening:
            break
        await asyncio.sleep(0.05)
    assert workers.a.is_listening

    await workers.a.stop_listener()
    assert workers.a.is_listening is False
    await workers.a.stop_listener()  # must not raise


async def test_a_publish_failure_never_prevents_local_delivery():
    """Local clients are served first and unconditionally.

    A notification failure must degrade cross-worker latency, never become a
    delivery failure for the worker that is already holding the connection.
    """
    room_id = str(uuid.uuid4())
    local = InProcessFanout()
    broken = PostgresNotifyFanout(local, "postgresql://nobody@127.0.0.1:1/nothing")
    socket = RecordingSocket()
    await local.register(Connection("c1", 1, 10, None, socket, {7: {room_id}}))

    delivered = await broken.publish(envelope(7, room_id, 4))
    assert delivered == 1
    assert len(socket.events()) == 1


# ===========================================================================
# Contract of the payload itself
# ===========================================================================


async def test_the_notify_payload_carries_identifiers_only():
    """NOTIFY is a wake-up signal, never the message.

    Two independent reasons, and both are asserted: `D6-P1` has decided no
    disclosure level, and PostgreSQL caps a NOTIFY payload at 8000 bytes - a
    design that carried content would fail on exactly the longest messages.
    """
    import asyncpg

    room_id = str(uuid.uuid4())
    received: list[str] = []
    conn = await asyncpg.connect(DSN)
    try:
        await conn.add_listener(CHANNEL, lambda *args: received.append(args[3]))
        local = InProcessFanout()
        publisher = PostgresNotifyFanout(local, DSN)
        await publisher.publish(envelope(7, room_id, 12))

        for _ in range(100):
            if received:
                break
            await asyncio.sleep(0.05)
        assert received, "no NOTIFY observed"

        payload = json.loads(received[0])
        assert set(payload) == {
            "origin", "event_id", "event_type", "family_id", "room_id",
            "message_id", "room_sequence", "occurred_at", "actor_type",
        }
        for forbidden in ("body", "text", "preview", "sender_name", "title"):
            assert forbidden not in payload
        assert len(received[0].encode()) <= MAX_PAYLOAD_BYTES
    finally:
        await conn.close()


def test_the_sqlalchemy_url_is_converted_to_a_plain_libpq_dsn():
    """The listener needs a raw connection; a pooled SQLAlchemy one must not be
    held open for the life of the process."""
    assert (
        to_asyncpg_dsn("postgresql+asyncpg://u:p@h:5432/db") == "postgresql://u:p@h:5432/db"
    )
    # Already-plain URLs pass through untouched.
    assert to_asyncpg_dsn("postgresql://u:p@h:5432/db") == "postgresql://u:p@h:5432/db"
