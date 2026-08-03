from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family import service as family_service
from app.dependencies import get_current_user
from . import service
from .schemas import ActivityLogEntryOut

router = APIRouter(tags=["family-activity-log"])


@router.get("/api/families/{family_id}/activity-log", response_model=list[ActivityLogEntryOut])
async def list_activity(
    family_id: int,
    limit: int = Query(default=100, ge=1, le=200),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await family_service.require_permission(db, user, family_id, family_service.FAMILY_MEMBERS_READ)
    return await service.list_activity(db, family_id, limit)
