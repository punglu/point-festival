from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family import service as family_service
from app.domains.family.dependencies import get_family_membership, require_family_permission
from app.domains.family.models import FamilyMembership
from . import service
from .schemas import FamilyRuleOut, FamilyRulesReplace

router = APIRouter(tags=["family-rules"])


@router.get("/api/families/{family_id}/rules", response_model=list[FamilyRuleOut])
async def list_rules(family_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.list_rules(db, family_id)


@router.put("/api/families/{family_id}/rules", response_model=list[FamilyRuleOut])
async def replace_rules(
    family_id: int,
    body: FamilyRulesReplace,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_MEMBERS_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    _account, actor = authorized
    return await service.replace_rules(db, family_id, actor, [entry.model_dump() for entry in body.rules])
