from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_family_membership
from app.domains.family.models import FamilyMembership
from . import service
from .schemas import SearchResultItem

router = APIRouter(tags=["family-search"])


@router.get("/api/families/{family_id}/search", response_model=list[SearchResultItem])
async def search(
    family_id: int,
    q: str = Query(min_length=1, max_length=100),
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    return await service.search(db, family_id, actor, q)
