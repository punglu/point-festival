from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_family_membership
from app.domains.family.models import FamilyMembership
from . import service
from .schemas import ScheduleEventCreate, ScheduleEventOut, ScheduleEventUpdate

router = APIRouter(tags=["family-schedule"])


@router.get("/api/families/{family_id}/schedule-events", response_model=list[ScheduleEventOut])
async def list_events(family_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.list_events(db, family_id)


@router.post("/api/families/{family_id}/schedule-events", response_model=ScheduleEventOut, status_code=status.HTTP_201_CREATED)
async def create_event(family_id: int, body: ScheduleEventCreate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.create_event(db, family_id, actor, **body.model_dump())


@router.get("/api/families/{family_id}/schedule-events/{event_id}", response_model=ScheduleEventOut)
async def get_event(family_id: int, event_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.get_event(db, family_id, event_id)


@router.patch("/api/families/{family_id}/schedule-events/{event_id}", response_model=ScheduleEventOut)
async def update_event(family_id: int, event_id: int, body: ScheduleEventUpdate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.update_event(db, family_id, event_id, body.model_dump(exclude_unset=True))


@router.delete("/api/families/{family_id}/schedule-events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(family_id: int, event_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    await service.delete_event(db, family_id, event_id)
