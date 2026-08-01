"""Wagle realtime transport: envelope, connection registry, fan-out port, resume.

Read this before changing anything here:

**The database is the source of truth. This module is a transport.** Nothing in
here is allowed to be the only place a message exists. A connection can be
dropped, a process can die, a fan-out can be missed — and no message is lost,
because every one of them is recoverable from `wagle_messages` by
`(room_id, sequence)`. That is the whole reason the envelope below carries
identifiers instead of content.

**Why the envelope has no message body.** It would be easy to inline it and
save the client a fetch. Two reasons not to:

1. There is no approved contract that says the realtime channel may carry
   message content, and `D6-P1` (payload disclosure) is undecided. Inventing a
   disclosure level here would be inventing policy.
2. It keeps one code path. The client materializes live messages through the
   same resume query it uses after a reconnect, so "live" and "recovered"
   cannot render differently — which is otherwise a standing source of bugs
   that only appear after a network blip.

**At-least-once, never exactly-once.** The same envelope may arrive more than
once: the dispatcher retries, a client may resume over a range it already has,
and a reconnect replays. Deduplication is the client's job and is trivial,
because `(room_id, sequence)` is unique and monotonic per room.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.family import service as family_service
from app.domains.family.models import Account, FamilyMembership
from app.domains.wagle.models import WagleMessage, WagleParticipant, WagleRoom

# Ordering is per (FamilyGroup, Room) via `wagle_messages.sequence`. There is
# deliberately no global counter: the Realtime Messaging Contract states global
# ordering "is not required and must not be built".
MAX_RESUME_BATCH = 200


@dataclass(frozen=True)
class RealtimeEnvelope:
    """Identifiers only — see the module docstring for why there is no body."""

    event_id: str
    event_type: str
    family_id: int
    room_id: str
    message_id: str
    room_sequence: int
    occurred_at: str
    # Distinguishes a human message from a Markpoint ServicePrincipal system
    # message without disclosing either one's content. The UI must be able to
    # tell them apart; the Service Principal must never look like a person.
    actor_type: str

    def as_event(self) -> dict:
        return {
            "type": "event",
            "event_id": self.event_id,
            "event_type": self.event_type,
            "family_id": self.family_id,
            "room_id": self.room_id,
            "message_id": self.message_id,
            "room_sequence": self.room_sequence,
            "occurred_at": self.occurred_at,
            "actor_type": self.actor_type,
        }


def envelope_from_outbox(event, *, room_id: str, room_sequence: int, actor_type: str) -> RealtimeEnvelope:
    """Build the wire envelope from a durable Outbox row.

    `source_event_id` is the message UUID (Wave 2 contract), so `event_id` and
    `message_id` are intentionally the same value: one durable message produces
    exactly one logical event, and a client that has the message has the event.
    """
    occurred = event.created_at or datetime.now(timezone.utc)
    return RealtimeEnvelope(
        event_id=str(event.source_event_id),
        event_type=event.event_type,
        family_id=event.family_id,
        room_id=str(room_id),
        message_id=str(event.source_event_id),
        room_sequence=room_sequence,
        occurred_at=occurred.astimezone(timezone.utc).isoformat(),
        actor_type=actor_type,
    )


class RealtimeFanoutPort(Protocol):
    """Seam between "an event became durable" and "connected clients hear it".

    It exists as a port because the correct implementation depends on a
    deployment decision that has not been made. See `InProcessFanout` for what
    v1 does and, more importantly, what it does not do.
    """

    async def publish(self, envelope: RealtimeEnvelope) -> int: ...


@dataclass
class Connection:
    """One physical WebSocket.

    `Account + Device + Session` is **one logical** subscription, but the
    Realtime Messaging Contract is explicit that multiple physical sockets may
    legitimately coexist (tabs, reconnects, connection replacement) and that no
    invariant may forbid them. So identity here is `connection_id`, not the
    session — several Connections can share one session_id and that is normal,
    not a leak to clean up.
    """

    connection_id: str
    account_id: int
    session_id: int
    device_id: str | None
    send: object  # awaitable callable(dict) -> None
    # family_id -> set of room_id strings this connection is authorized for and
    # has asked to receive. Server-derived: see `authorize_subscription`.
    subscriptions: dict[int, set[str]] = field(default_factory=dict)

    def is_subscribed(self, family_id: int, room_id: str) -> bool:
        return room_id in self.subscriptions.get(family_id, set())

    def drop_family(self, family_id: int) -> None:
        self.subscriptions.pop(family_id, None)

    def drop_room(self, family_id: int, room_id: str) -> None:
        rooms = self.subscriptions.get(family_id)
        if rooms:
            rooms.discard(room_id)
            if not rooms:
                self.subscriptions.pop(family_id, None)


class InProcessFanout:
    """v1 fan-out: an in-process registry of live connections.

    **Known boundary, recorded rather than hidden.** This reaches only the
    connections held by *this* process. `docker-compose.prod.yml` runs
    `uvicorn --workers 2`, so in production a message committed on worker A
    does not fan out to a client attached to worker B.

    That is a latency limitation, not a correctness one, and the difference
    matters: every client also runs a durable catch-up against
    `resume_missed_events()` on its own cursor, so a missed fan-out is
    recovered from the database on the next tick. No message is lost on any
    worker; a cross-worker message is simply delivered on the catch-up interval
    instead of instantly.

    Closing the latency gap needs a cross-process channel (PostgreSQL
    LISTEN/NOTIFY, or a broker). Both are real options and neither is chosen
    here, because no approved document selects one and this task is forbidden
    from introducing infrastructure without that basis. The port above is the
    seam where that choice plugs in.
    """

    def __init__(self) -> None:
        self._connections: dict[str, Connection] = {}
        self._lock = asyncio.Lock()

    async def register(self, connection: Connection) -> None:
        async with self._lock:
            self._connections[connection.connection_id] = connection

    async def unregister(self, connection_id: str) -> None:
        async with self._lock:
            self._connections.pop(connection_id, None)

    async def get(self, connection_id: str) -> Connection | None:
        async with self._lock:
            return self._connections.get(connection_id)

    async def connections_for_account(self, account_id: int) -> list[Connection]:
        async with self._lock:
            return [c for c in self._connections.values() if c.account_id == account_id]

    async def publish(self, envelope: RealtimeEnvelope) -> int:
        """Deliver to every locally-connected subscriber. Returns the count.

        One failing socket must never suppress delivery to the others, so each
        send is isolated: a raise is swallowed per connection and that
        connection is dropped, which is also the failure-isolation requirement
        (one device's failure never blocks another device or another Family).
        """
        async with self._lock:
            targets = [
                c
                for c in self._connections.values()
                if c.is_subscribed(envelope.family_id, envelope.room_id)
            ]
        payload = envelope.as_event()
        delivered = 0
        for connection in targets:
            try:
                await connection.send(payload)
                delivered += 1
            except Exception:
                await self.unregister(connection.connection_id)
        return delivered

    async def revoke_family(self, account_id: int, family_id: int) -> int:
        """Membership in one Family ended: drop only that Family's rooms.

        The Account keeps its Session and every other Family. Closing the whole
        connection here would turn "you left one family" into "you were logged
        out", which D1/D3 explicitly forbid.
        """
        affected = 0
        for connection in await self.connections_for_account(account_id):
            if family_id in connection.subscriptions:
                connection.drop_family(family_id)
                affected += 1
                try:
                    await connection.send(
                        {"type": "subscription_revoked", "family_id": family_id, "reason": "membership"}
                    )
                except Exception:
                    await self.unregister(connection.connection_id)
        return affected

    async def revoke_session(self, session_id: int) -> int:
        """The Session itself is gone: every connection on it must close."""
        async with self._lock:
            targets = [c for c in self._connections.values() if c.session_id == session_id]
        for connection in targets:
            try:
                await connection.send({"type": "session_revoked", "reason": "session"})
            except Exception:
                pass
            await self.unregister(connection.connection_id)
        return len(targets)


# Module-level singleton: the web process's own registry. The dispatcher in the
# same process publishes into it; a separate worker process has its own.
fanout = InProcessFanout()


async def authorized_family_ids(db: AsyncSession, account_id: int) -> set[int]:
    """The server-derived AuthorizedFamilySet.

    Never `activeFamilyId` from the client. The client's active family is a UI
    convenience; using it as a subscription filter would let a client both
    over-subscribe (ask for a family it cannot see) and under-subscribe (miss
    events from its other families, which D1 forbids).
    """
    pairs = await family_service.authorized_family_set(db, account_id)
    return {family.id for family, _membership in pairs}


async def authorize_subscription(
    db: AsyncSession, account: Account, family_id: int, room_id: str
) -> tuple[FamilyMembership, WagleRoom, WagleParticipant]:
    """Re-derive, from the database, whether this Account may hear this room.

    Every layer is checked again on every subscribe, in this order, because
    each answers a different question and none implies another:

    1. ACTIVE membership in that Family (the Account may have left).
    2. The room exists **in that Family** (a valid room id from another family
       is exactly what a cross-family probe looks like).
    3. An ACTIVE participant row for this membership (membership in the family
       is not membership in the room).

    Raises `PermissionError` for all three, deliberately: distinguishing "no
    such room" from "not allowed" would confirm the existence of another
    family's room to a caller who cannot see it.

    The membership check is normalized to `PermissionError` too. It natively
    raises `HTTPException(403)`, which is right for a route but wrong here —
    this function is called from the WebSocket loop and the catch-up loop as
    well as from routes, and a single failure type is what lets all three
    handle denial the same way instead of each guessing which one to catch.
    """
    try:
        membership = await family_service.get_active_membership(db, account.id, family_id)
    except Exception:
        raise PermissionError("family not accessible")

    try:
        room_uuid = UUID(str(room_id))
    except (ValueError, AttributeError, TypeError):
        raise PermissionError("room not accessible")

    room = (
        await db.execute(
            select(WagleRoom).where(
                WagleRoom.id == room_uuid,
                WagleRoom.family_group_id == family_id,
                WagleRoom.deleted_at.is_(None),
            )
        )
    ).scalars().first()
    if room is None:
        raise PermissionError("room not accessible")

    participant = (
        await db.execute(
            select(WagleParticipant).where(
                WagleParticipant.room_id == room.id,
                WagleParticipant.family_membership_id == membership.id,
                WagleParticipant.status == "active",
            )
        )
    ).scalars().first()
    if participant is None:
        raise PermissionError("room not accessible")

    return membership, room, participant


async def resume_missed_events(
    db: AsyncSession,
    account: Account,
    family_id: int,
    room_id: str,
    after_sequence: int,
    limit: int = MAX_RESUME_BATCH,
) -> dict:
    """Everything durably recorded in this room after `after_sequence`.

    This is the recovery path and it is deliberately the *same* query the live
    path resolves against. Authorization is re-derived here rather than trusted
    from the connection, because a connection can outlive the membership that
    justified it.

    `has_more` is returned instead of silently truncating: a client that slept
    through more than one batch must page rather than skip, or the gap it was
    recovering from is simply moved further along.
    """
    _membership, room, participant = await authorize_subscription(db, account, family_id, room_id)

    bounded = max(1, min(int(limit), MAX_RESUME_BATCH))
    cursor = max(0, int(after_sequence))

    # A participant only ever sees from where it joined. Resuming from 0 must
    # not become a way to read a room's history from before you were added.
    floor_sequence = max(cursor, int(participant.joined_sequence) - 1)

    stmt = (
        select(WagleMessage)
        .where(
            WagleMessage.room_id == room.id,
            WagleMessage.family_group_id == family_id,
            WagleMessage.sequence > floor_sequence,
        )
        .order_by(WagleMessage.sequence)
        .limit(bounded + 1)
    )
    rows = list((await db.execute(stmt)).scalars())
    has_more = len(rows) > bounded
    rows = rows[:bounded]

    events = [
        {
            "event_id": str(row.id),
            "event_type": "wagle.message.created",
            "family_id": family_id,
            "room_id": str(room.id),
            "message_id": str(row.id),
            "room_sequence": int(row.sequence),
            "occurred_at": row.created_at.astimezone(timezone.utc).isoformat(),
            "actor_type": "SERVICE" if row.message_type == "SERVICE_ACTION" else "ACCOUNT",
        }
        for row in rows
    ]
    return {
        "family_id": family_id,
        "room_id": str(room.id),
        "from_sequence": floor_sequence,
        "next_sequence": events[-1]["room_sequence"] if events else floor_sequence,
        "room_next_sequence": int(room.next_message_sequence),
        "events": events,
        "has_more": has_more,
    }


async def revalidate_connection(db: AsyncSession, connection: Connection) -> dict:
    """Re-derive a live connection's authority from the database.

    Called on a bounded interval rather than only at connect, because authority
    can be withdrawn while a socket stays open. Returns what changed so the
    caller can tell the client which specific Families it lost, instead of
    silently going quiet.

    The revocation semantics are asymmetric on purpose:

    - Session revoked or Account no longer usable -> the connection dies.
    - One Family's membership ended -> only that Family's subscriptions go.
      Every other Family keeps working.
    """
    from app.domains.family import auth_service

    try:
        session_row = await auth_service.load_active_session(db, connection.session_id)
    except Exception:
        return {"terminate": True, "reason": "session"}
    if session_row.account_id != connection.account_id:
        return {"terminate": True, "reason": "session"}

    account = await db.get(Account, connection.account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        return {"terminate": True, "reason": "account"}

    allowed = await authorized_family_ids(db, connection.account_id)
    revoked_families = [fid for fid in list(connection.subscriptions) if fid not in allowed]
    for family_id in revoked_families:
        connection.drop_family(family_id)

    revoked_rooms: list[tuple[int, str]] = []
    for family_id, rooms in list(connection.subscriptions.items()):
        for room_id in list(rooms):
            try:
                await authorize_subscription(db, account, family_id, room_id)
            except Exception:
                connection.drop_room(family_id, room_id)
                revoked_rooms.append((family_id, room_id))

    return {
        "terminate": False,
        "revoked_families": revoked_families,
        "revoked_rooms": revoked_rooms,
    }


def subscribed_pairs(connection: Connection) -> Iterable[tuple[int, str]]:
    for family_id, rooms in connection.subscriptions.items():
        for room_id in rooms:
            yield family_id, room_id
