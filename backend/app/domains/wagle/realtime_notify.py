"""Cross-worker realtime wake-up over PostgreSQL LISTEN/NOTIFY.

MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001, on PM approval of LISTEN/NOTIFY as the
mechanism. No Redis, Kafka or NATS: the database this system already depends on
is the channel, so nothing new has to be deployed, secured or kept alive.

**NOTIFY is a wake-up signal. It is never the message.** The database and the
Transactional Outbox stay the source of truth, and everything here is designed
so that losing every single notification changes latency and nothing else:

- The payload carries **identifiers only** — no body, no sender, no room title.
  Partly because `D6-P1` has not decided any disclosure level, and partly
  because a NOTIFY payload is capped at 8000 bytes, so a design that carried
  content would fail on exactly the messages users care most about.
- A missed, duplicated or reordered notification is recovered by the durable
  cursor catch-up that every connection already runs. That fallback is **not**
  removed now that NOTIFY exists; it is what makes NOTIFY optional.
- A successful NOTIFY says nothing about whether a user received anything, and
  is never surfaced as a delivery state.

Ordering is still per `(FamilyGroup, Room)` via the room sequence. NOTIFY
delivery order is not relied upon anywhere, and no global order is claimed.
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid

import asyncpg

from app.domains.wagle.realtime import InProcessFanout, RealtimeEnvelope

CHANNEL = "wagle_realtime"

# PostgreSQL rejects a NOTIFY payload over 8000 bytes. Ours is a handful of
# identifiers and cannot approach that, but a malformed caller must fail here
# rather than at the database with a transaction-level error.
MAX_PAYLOAD_BYTES = 7000

_RECONNECT_BASE_SECONDS = 0.5
_RECONNECT_MAX_SECONDS = 30.0


def to_asyncpg_dsn(database_url: str) -> str:
    """SQLAlchemy URL -> plain libpq DSN.

    The listener needs a raw asyncpg connection: `add_listener` keeps a
    dedicated session open for the lifetime of the process, which is exactly
    what a pooled SQLAlchemy connection must not do.
    """
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


class PostgresNotifyFanout:
    """`RealtimeFanoutPort` that reaches every ASGI worker, not just this one.

    Two halves:

    - `publish()` delivers to this process's own connections **and** emits a
      NOTIFY so the other workers can do the same.
    - `start_listener()` holds a dedicated connection LISTENing on the channel
      and hands anything it hears to the local registry.

    `origin_id` is why the publishing worker does not deliver twice: it stamps
    each notification with its own process identity and its own listener drops
    what it recognises. Client-side dedup on `(room_id, room_sequence)` would
    have covered it anyway, but relying on the client to clean up a duplicate
    the server knowingly created is the wrong default.
    """

    def __init__(self, local: InProcessFanout, dsn: str) -> None:
        self._local = local
        self._dsn = dsn
        # Unique per process. PID alone is not enough: two containers on one
        # host can share a PID number.
        self.origin_id = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
        self._listen_conn: asyncpg.Connection | None = None
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self.received = 0
        self.skipped_own = 0

    # -- publish ----------------------------------------------------------

    async def publish(self, envelope: RealtimeEnvelope) -> int:
        """Deliver locally, then wake the other workers.

        The local delivery happens **first and unconditionally**. If NOTIFY
        fails — the database is briefly unreachable, the connection is being
        recycled — the clients attached to this worker have still been served,
        and the ones elsewhere fall back to their catch-up. A notification
        failure must never become a delivery failure.
        """
        delivered = await self._local.publish(envelope)
        try:
            await self._notify(envelope)
        except Exception:
            # Swallowed on purpose: see the docstring. The Outbox row is only
            # marked published by the dispatcher, which has already succeeded
            # in making the message durable.
            pass
        return delivered

    async def _notify(self, envelope: RealtimeEnvelope) -> None:
        payload = json.dumps(
            {
                "origin": self.origin_id,
                "event_id": envelope.event_id,
                "event_type": envelope.event_type,
                "family_id": envelope.family_id,
                "room_id": envelope.room_id,
                "message_id": envelope.message_id,
                "room_sequence": envelope.room_sequence,
                "occurred_at": envelope.occurred_at,
                "actor_type": envelope.actor_type,
            },
            separators=(",", ":"),
        )
        if len(payload.encode()) > MAX_PAYLOAD_BYTES:
            # Cannot happen with identifiers, but if it ever does the correct
            # answer is to send nothing and let the durable catch-up handle it
            # rather than to truncate an envelope into something misleading.
            return
        conn = await asyncpg.connect(self._dsn)
        try:
            await conn.execute("SELECT pg_notify($1, $2)", CHANNEL, payload)
        finally:
            await conn.close()

    # -- listen -----------------------------------------------------------

    def _on_notify(self, _conn, _pid, _channel, payload: str) -> None:
        """asyncpg calls this synchronously; do the work on the loop."""
        try:
            data = json.loads(payload)
        except Exception:
            return
        if data.get("origin") == self.origin_id:
            # Our own publish already delivered this locally.
            self.skipped_own += 1
            return
        self.received += 1
        envelope = RealtimeEnvelope(
            event_id=str(data.get("event_id", "")),
            event_type=str(data.get("event_type", "")),
            family_id=int(data.get("family_id", 0)),
            room_id=str(data.get("room_id", "")),
            message_id=str(data.get("message_id", "")),
            room_sequence=int(data.get("room_sequence", 0)),
            occurred_at=str(data.get("occurred_at", "")),
            actor_type=str(data.get("actor_type", "ACCOUNT")),
        )
        asyncio.create_task(self._local.publish(envelope))

    async def start_listener(self) -> None:
        """Open the dedicated LISTEN connection and keep it open.

        Reconnects with backoff if the connection drops — a listener that dies
        quietly is the worst outcome here, because the worker would look
        healthy while silently serving only its own traffic. Nothing is
        replayed on reconnect: notifications missed while down are recovered by
        the durable cursor, which is the same mechanism that covers every other
        gap.
        """
        self._stop.clear()
        self._task = asyncio.create_task(self._listen_loop())

    async def _listen_loop(self) -> None:
        attempt = 0
        while not self._stop.is_set():
            try:
                self._listen_conn = await asyncpg.connect(self._dsn)
                await self._listen_conn.add_listener(CHANNEL, self._on_notify)
                attempt = 0
                # Hold the connection open until asked to stop or it breaks.
                while not self._stop.is_set():
                    try:
                        await asyncio.wait_for(self._stop.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        if self._listen_conn.is_closed():
                            raise ConnectionError("listener connection closed")
            except Exception:
                delay = min(_RECONNECT_BASE_SECONDS * 2**attempt, _RECONNECT_MAX_SECONDS)
                attempt += 1
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
            finally:
                if self._listen_conn is not None and not self._listen_conn.is_closed():
                    try:
                        await self._listen_conn.remove_listener(CHANNEL, self._on_notify)
                        await self._listen_conn.close()
                    except Exception:
                        pass
                self._listen_conn = None

    async def stop_listener(self) -> None:
        self._stop.set()
        if self._task is not None:
            try:
                await asyncio.wait_for(self._task, timeout=5)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                self._task.cancel()
        self._task = None

    @property
    def is_listening(self) -> bool:
        return self._listen_conn is not None and not self._listen_conn.is_closed()
