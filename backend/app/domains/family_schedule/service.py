"""Family Schedule application service. Any active Family member may
create/view/edit/delete -- a shared family calendar, same collaborative
shape as SLICE-TODO, not an admin-gated capability."""
from __future__ import annotations
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family.models import FamilyMembership
from .models import FamilyScheduleEvent


async def _validate_attendees(db: AsyncSession, family_id: int, membership_ids: list[int] | None) -> None:
    if not membership_ids:
        return
    rows = (
        await db.execute(
            select(FamilyMembership.id).where(
                FamilyMembership.id.in_(membership_ids),
                FamilyMembership.family_group_id == family_id,
                FamilyMembership.status == "active",
                FamilyMembership.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    if set(rows) != set(membership_ids):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="참석자는 활성 가족 구성원만 지정할 수 있습니다")


async def list_events(db: AsyncSession, family_id: int) -> list[FamilyScheduleEvent]:
    stmt = select(FamilyScheduleEvent).where(FamilyScheduleEvent.family_group_id == family_id).order_by(FamilyScheduleEvent.starts_at)
    return list((await db.execute(stmt)).scalars())


async def create_event(db: AsyncSession, family_id: int, actor: FamilyMembership, **fields) -> FamilyScheduleEvent:
    await _validate_attendees(db, family_id, fields.get("attendee_membership_ids"))
    event = FamilyScheduleEvent(family_group_id=family_id, created_by_membership_id=actor.id, **fields)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def _get(db: AsyncSession, family_id: int, event_id: int) -> FamilyScheduleEvent:
    event = await db.get(FamilyScheduleEvent, event_id)
    if event is None or event.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없습니다")
    return event


async def get_event(db: AsyncSession, family_id: int, event_id: int) -> FamilyScheduleEvent:
    return await _get(db, family_id, event_id)


async def update_event(db: AsyncSession, family_id: int, event_id: int, updates: dict) -> FamilyScheduleEvent:
    event = await _get(db, family_id, event_id)
    if "attendee_membership_ids" in updates and updates["attendee_membership_ids"] is not None:
        await _validate_attendees(db, family_id, updates["attendee_membership_ids"])
    for key, value in updates.items():
        if value is not None:
            setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, family_id: int, event_id: int) -> None:
    event = await _get(db, family_id, event_id)
    await db.delete(event)
    await db.commit()
