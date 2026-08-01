"""Dedicated Outbox delivery Worker: `python -m app.workers.service_outbox`.

Not a Web-process background task - a standalone, independently restartable
process so its own crash/backpressure never affects request-serving uptime,
and its own concurrency (multiple replicas) never needs anything beyond what
service_outbox.service.claim_batch's FOR UPDATE SKIP LOCKED already gives it.

Delivery contract: at-least-once from this Worker's side, made safe by
Wagle's own idempotent SERVICE_ACTION ingress on the receiving side -
publish_service_action() is called in-process (never over HTTP with a Bearer
credential) because this Worker already holds a trusted ServicePrincipal row
loaded directly from the database, the same trust boundary any other
in-process caller in this codebase relies on.
"""
from __future__ import annotations

import asyncio
import signal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.wagle import service as wagle_service
from app.domains.wagle.schemas import ServiceActionPublish
from app.domains.service_outbox import service as outbox_service
from app.domains.service_outbox.models import ServiceOutboxEvent

# What each owning service is allowed to publish, and what this Worker calls
# itself when it (idempotently) provisions that service's own Principal.
# Adding a second owning service means adding one entry here - no other
# Worker code changes.
ALLOWED_ACTIONS_BY_OWNER: dict[str, list[dict]] = {
    "mark-point": [{"action_type": "mission.completed", "schema_version": 1}],
}
PRINCIPAL_DISPLAY_NAME_BY_OWNER: dict[str, str] = {
    "mark-point": "Mark Point",
}

DEFAULT_BATCH_SIZE = 10
DEFAULT_POLL_INTERVAL_SECONDS = 2.0


async def _principal_for(db: AsyncSession, owner_service: str):
    display_name = PRINCIPAL_DISPLAY_NAME_BY_OWNER.get(owner_service, owner_service)
    return await wagle_service.bootstrap_service_principal(db, owner_service, display_name)


async def process_one(db: AsyncSession, event: ServiceOutboxEvent) -> str:
    """Delivers a single claimed row. Returns 'published', 'retry_scheduled',
    or 'dead' for logging/tests - never raises, since one bad row must never
    take the rest of the batch down with it."""
    try:
        principal = await _principal_for(db, event.owner_service)
        allowed_actions = ALLOWED_ACTIONS_BY_OWNER.get(event.owner_service, [])
        binding = await wagle_service.ensure_canonical_service_binding(db, principal, event.family_id, allowed_actions)
        publish_data = ServiceActionPublish(
            room_id=binding.room_id,
            action_type=event.event_type,
            schema_version=event.event_version,
            source=event.owner_service,
            source_event_id=event.source_event_id,
            snapshot=event.payload,
        )
        # Durable the instant this returns, whether newly created or an
        # idempotent replay - a crash on the next line still leaves exactly
        # one Wagle message, and the next attempt marks this row PUBLISHED.
        await wagle_service.publish_service_action(db, principal, event.family_id, publish_data)
        await outbox_service.mark_published(db, event)
        return "published"
    except HTTPException as exc:
        await db.rollback()
        await outbox_service.record_failure(db, event, f"http_{exc.status_code}")
    except Exception:
        await db.rollback()
        await outbox_service.record_failure(db, event, "worker_error")
    return "dead" if event.status == "DEAD" else "retry_scheduled"


async def run_once(db: AsyncSession, batch_size: int = DEFAULT_BATCH_SIZE) -> dict:
    """Drain one batch of SERVICE_ACTION rows.

    Claims are now scoped to the owners this Worker actually knows how to
    publish. MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001: before this, the
    claim was unfiltered, so once Wave 2 started writing `owner_service="wagle"`
    delivery events this Worker picked them up and tried to publish a human
    message as a Service Action - provisioning a bogus `wagle` ServicePrincipal
    and retrying the row to DEAD. Wagle's own rows belong to
    `app.workers.wagle_realtime`.
    """
    outcomes = {"published": 0, "retry_scheduled": 0, "dead": 0}
    total_claimed = 0
    for owner_service in ALLOWED_ACTIONS_BY_OWNER:
        claimed = await outbox_service.claim_batch(
            db, batch_size=batch_size, owner_service=owner_service
        )
        total_claimed += len(claimed)
        for event in claimed:
            outcome = await process_one(db, event)
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
    return {"claimed": total_claimed, **outcomes}


async def main_loop(poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS) -> None:
    from app.database import AsyncSessionLocal

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass  # signal handlers are not available on every platform (e.g. some test runners)

    print("[service_outbox] worker starting")
    while not stop.is_set():
        async with AsyncSessionLocal() as db:
            result = await run_once(db)
        if result["claimed"]:
            print(f"[service_outbox] batch: {result}")
        if result["claimed"] == 0:
            try:
                await asyncio.wait_for(stop.wait(), timeout=poll_interval_seconds)
            except asyncio.TimeoutError:
                pass
    print("[service_outbox] worker stopped")


if __name__ == "__main__":
    asyncio.run(main_loop())
