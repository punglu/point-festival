"""Wagle realtime dispatcher: drains `wagle.message.created` Outbox rows.

This is the consumer Wave 2 deliberately did not write. Wave 2 made the event
durable inside the message transaction; this turns a durable row into a
WebSocket fan-out and a Push attempt.

**It never writes a message and never rolls one back.** A delivery failure is
recorded against the Outbox row only. If this module could delete or reverse a
`wagle_messages` row, a transient push failure would become data loss — which
is the exact inversion the transactional-outbox pattern exists to prevent.

**Separate transaction from the send.** The sender's transaction committed long
before this runs; that is what makes "the message is safe" independent of "the
notification went out".

It shares `claim_batch()` with the existing SERVICE_ACTION worker rather than
introducing a second claim mechanism: `FOR UPDATE SKIP LOCKED` already gives
concurrent-worker safety and lease-based crash recovery, and a second scheme
would have to be kept consistent with the first forever.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.family.models import FamilyMembership
from app.domains.service_outbox import service as outbox_service
from app.domains.service_outbox.models import ServiceOutboxEvent
from app.domains.wagle import push_service
from app.domains.wagle import service as wagle_service
from app.domains.wagle.models import WagleMessage, WagleParticipant
from app.domains.wagle.realtime import RealtimeFanoutPort, envelope_from_outbox, fanout

# This dispatcher owns exactly one event type. The SERVICE_ACTION worker
# (`app/workers/service_outbox.py`) owns `mark-point`'s rows. Splitting by
# `owner_service` keeps one consumer's failure from stalling the other's queue.
OWNER_SERVICE = wagle_service.SERVICE_CODE
HANDLED_EVENT_TYPES = {wagle_service.MESSAGE_CREATED_EVENT_TYPE}


async def _load_message(db: AsyncSession, event: ServiceOutboxEvent) -> WagleMessage | None:
    """Resolve the durable message this event refers to.

    `source_event_id` is the message UUID by Wave 2 contract. A missing row is
    not retried forever — see `process_event`.
    """
    return (
        await db.execute(
            select(WagleMessage).where(
                WagleMessage.id == event.source_event_id,
                WagleMessage.family_group_id == event.family_id,
            )
        )
    ).scalars().first()


async def _recipient_account_ids(
    db: AsyncSession, message: WagleMessage, family_id: int
) -> list[int]:
    """Accounts that should hear about this message.

    Derived from the room's own ACTIVE participants, joined to ACTIVE
    memberships, so a participant whose family membership was suspended stops
    being a recipient without any separate bookkeeping.

    The sender is excluded: they already know. Doing this in SQL rather than in
    the client avoids a self-notification that every client would then have to
    learn to ignore.
    """
    stmt = (
        select(FamilyMembership.account_id)
        .join(WagleParticipant, WagleParticipant.family_membership_id == FamilyMembership.id)
        .where(
            WagleParticipant.room_id == message.room_id,
            WagleParticipant.status == "active",
            FamilyMembership.family_group_id == family_id,
            FamilyMembership.status == "active",
        )
    )
    if message.sender_participant_id is not None:
        stmt = stmt.where(WagleParticipant.id != message.sender_participant_id)
    return [int(x) for x in (await db.execute(stmt)).scalars() if x is not None]


async def process_event(
    db: AsyncSession,
    event: ServiceOutboxEvent,
    *,
    port: RealtimeFanoutPort | None = None,
) -> dict:
    """Deliver one claimed Outbox row. Never raises.

    One malformed or undeliverable row must not take the rest of the batch
    down with it — that is the per-event failure isolation requirement, and the
    reason every outcome below is a return value rather than an exception.
    """
    port = port or fanout
    if event.event_type not in HANDLED_EVENT_TYPES:
        # Not ours. Leave it PENDING for its own consumer instead of marking it
        # published, which would silently swallow another service's event.
        return {"outcome": "skipped_foreign_event", "delivered": 0}

    message = await _load_message(db, event)
    if message is None:
        # The event references a message that does not exist. Retrying cannot
        # fix that, so let the existing bounded-retry path carry it to DEAD
        # rather than looping until the end of time.
        await outbox_service.record_failure(db, event, "message_missing")
        return {"outcome": "message_missing", "delivered": 0}

    actor_type = "SERVICE" if message.message_type == "SERVICE_ACTION" else "ACCOUNT"
    envelope = envelope_from_outbox(
        event,
        room_id=str(message.room_id),
        room_sequence=int(message.sequence),
        actor_type=actor_type,
    )

    delivered = 0
    push_stats: dict = {}
    try:
        delivered = await port.publish(envelope)
        recipients = await _recipient_account_ids(db, message, event.family_id)
        push_stats = await push_service.deliver_event(
            db, envelope, outbox_event_id=int(event.id), recipient_account_ids=recipients
        )
    except Exception:
        await db.rollback()
        await outbox_service.record_failure(db, event, "realtime_dispatch_error")
        return {"outcome": "retry_scheduled", "delivered": delivered}

    await outbox_service.mark_published(db, event)
    return {
        "outcome": "published",
        "delivered": delivered,
        "push": push_stats,
        "room_sequence": envelope.room_sequence,
    }


async def run_once(
    db: AsyncSession, *, batch_size: int = 20, port: RealtimeFanoutPort | None = None
) -> dict:
    """Claim and deliver one batch.

    Safe to call repeatedly and safe to call concurrently: `claim_batch` leases
    rows with `FOR UPDATE SKIP LOCKED`, and a process that dies mid-delivery
    has its lease expire and its rows re-claimed by the next run. Re-delivery
    is expected and harmless — clients dedupe on `(room_id, room_sequence)` and
    Push dedupes on `(outbox_event_id, subscription_id)`.
    """
    # Claim only Wagle's own rows. The SERVICE_ACTION Worker claims `mark-point`
    # rows the same way; neither can starve or mis-handle the other's queue.
    claimed = await outbox_service.claim_batch(
        db, batch_size=batch_size, owner_service=OWNER_SERVICE
    )

    outcomes: dict[str, int] = {}
    total_delivered = 0
    for event in claimed:
        result = await process_event(db, event, port=port)
        outcomes[result["outcome"]] = outcomes.get(result["outcome"], 0) + 1
        total_delivered += int(result.get("delivered", 0))

    return {"claimed": len(claimed), "delivered": total_delivered, **outcomes}
