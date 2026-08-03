"""Family Activity Log service. **No new event-logging table** -- reads
from `MarkpointAuditEvent` (already exists, already written by every
mission/ledger/config mutation) rather than duplicating it into a
parallel log, per the Phase D Slice Mapping's own design recommendation.
Read-only: nothing here can go stale relative to its source because it
never copies it."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family import service as family_service
from app.domains.family.models import FamilyMembership
from app.domains.markpoint_target import service as markpoint_service


async def list_activity(db: AsyncSession, family_id: int, limit: int = 100) -> list[dict]:
    events = await markpoint_service.list_audit_events(db, family_id, limit)

    actor_ids = {e.actor_membership_id for e in events if e.actor_membership_id is not None}
    name_by_membership_id: dict[int, str] = {}
    for membership_id in actor_ids:
        membership = await db.get(FamilyMembership, membership_id)
        if membership is not None:
            account = await family_service.get_account(db, membership.account_id)
            if account is not None:
                name_by_membership_id[membership_id] = account.display_name

    return [
        {
            "actor_membership_id": e.actor_membership_id,
            "actor_display_name": name_by_membership_id.get(e.actor_membership_id) if e.actor_membership_id else None,
            "action": e.action,
            "aggregate_type": e.aggregate_type,
            "payload": e.payload or {},
            "occurred_at": e.created_at,
        }
        for e in events
    ]
