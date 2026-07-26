"""Transactional Outbox: enqueue (same transaction as the business write),
claim (PostgreSQL FOR UPDATE SKIP LOCKED - safe across concurrent Worker
processes, no process-local lock), and record delivery outcome.

This module never talks to Doran or any other consumer - see
app/workers/service_outbox.py for the Worker that drains this table.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.service_outbox.models import ServiceOutboxEvent

MAX_ATTEMPTS = 8
BASE_BACKOFF_SECONDS = 30
MAX_BACKOFF_SECONDS = 3600
DEFAULT_LEASE_SECONDS = 30


def compute_backoff_seconds(attempt_count: int) -> int:
    return min(BASE_BACKOFF_SECONDS * (2 ** max(attempt_count - 1, 0)), MAX_BACKOFF_SECONDS)


async def enqueue_event(
    db: AsyncSession,
    *,
    owner_service: str,
    event_type: str,
    event_version: int,
    aggregate_type: str,
    aggregate_id: str,
    source_event_id: str,
    family_id: int,
    payload: dict,
) -> ServiceOutboxEvent:
    """Appends one Outbox row in the caller's own transaction. The caller
    commits (or rolls back) - this function never does either, so a rollback
    of the surrounding business transaction takes the Outbox row with it.

    Idempotent per (owner_service, source_event_id): a retried business call
    that reaches this again returns the row already recorded on the first
    attempt instead of creating a duplicate.
    """
    existing = (
        await db.execute(
            select(ServiceOutboxEvent).where(
                ServiceOutboxEvent.owner_service == owner_service,
                ServiceOutboxEvent.source_event_id == source_event_id,
            )
        )
    ).scalars().first()
    if existing is not None:
        return existing

    event = ServiceOutboxEvent(
        owner_service=owner_service,
        event_type=event_type,
        event_version=event_version,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        source_event_id=source_event_id,
        family_id=family_id,
        payload=payload,
    )
    try:
        async with db.begin_nested():
            db.add(event)
            await db.flush()
    except IntegrityError:
        # A concurrent enqueue for the exact same business event won the
        # race; a SAVEPOINT keeps this local to the nested block so the
        # caller's own transaction (e.g. the mission-completion write) is
        # untouched.
        existing = (
            await db.execute(
                select(ServiceOutboxEvent).where(
                    ServiceOutboxEvent.owner_service == owner_service,
                    ServiceOutboxEvent.source_event_id == source_event_id,
                )
            )
        ).scalars().one()
        return existing
    return event


async def claim_batch(
    db: AsyncSession, *, batch_size: int = 10, lease_seconds: int = DEFAULT_LEASE_SECONDS
) -> list[ServiceOutboxEvent]:
    """Atomically claims up to `batch_size` deliverable rows: PENDING rows due
    for (re)attempt, plus PROCESSING rows whose lease has expired (a Worker
    died mid-delivery). FOR UPDATE SKIP LOCKED means a second Worker running
    this concurrently simply skips rows already claimed instead of blocking
    or double-claiming - no in-process lock involved."""
    now = datetime.now(timezone.utc)
    ids_stmt = (
        select(ServiceOutboxEvent.id)
        .where(
            or_(
                and_(ServiceOutboxEvent.status == "PENDING", ServiceOutboxEvent.next_attempt_at <= now),
                and_(ServiceOutboxEvent.status == "PROCESSING", ServiceOutboxEvent.locked_until < now),
            )
        )
        .order_by(ServiceOutboxEvent.created_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )
    ids = list((await db.execute(ids_stmt)).scalars())
    if not ids:
        await db.commit()
        return []

    lease_until = now + timedelta(seconds=lease_seconds)
    await db.execute(
        update(ServiceOutboxEvent)
        .where(ServiceOutboxEvent.id.in_(ids))
        .values(status="PROCESSING", locked_until=lease_until)
    )
    await db.commit()
    rows = list(
        (await db.execute(select(ServiceOutboxEvent).where(ServiceOutboxEvent.id.in_(ids)).order_by(ServiceOutboxEvent.created_at))).scalars()
    )
    return rows


async def mark_published(db: AsyncSession, event: ServiceOutboxEvent) -> None:
    event.status = "PUBLISHED"
    event.published_at = datetime.now(timezone.utc)
    event.locked_until = None
    event.last_error_code = None
    await db.commit()


async def record_failure(db: AsyncSession, event: ServiceOutboxEvent, error_code: str) -> None:
    """Bounded retry with exponential backoff; DEAD once MAX_ATTEMPTS is
    exceeded so a permanently-undeliverable row stops being retried forever."""
    event.attempt_count += 1
    event.last_error_code = error_code[:60]
    event.locked_until = None
    if event.attempt_count >= MAX_ATTEMPTS:
        event.status = "DEAD"
    else:
        event.status = "PENDING"
        event.next_attempt_at = datetime.now(timezone.utc) + timedelta(
            seconds=compute_backoff_seconds(event.attempt_count)
        )
    await db.commit()
