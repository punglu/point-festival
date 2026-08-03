from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_family_membership
from app.domains.family.models import FamilyMembership
from . import service
from .schemas import RedemptionOut, RedemptionRequest, RewardCreate, RewardOut, RewardUpdate

router = APIRouter(tags=["reward-catalog"])


@router.get("/api/families/{family_id}/rewards", response_model=list[RewardOut])
async def list_rewards(family_id: int, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.list_rewards(db, family_id, actor)


@router.post("/api/families/{family_id}/rewards", response_model=RewardOut, status_code=status.HTTP_201_CREATED)
async def create_reward(family_id: int, body: RewardCreate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.create_reward(db, family_id, actor, name=body.name, cost=body.cost)


@router.patch("/api/families/{family_id}/rewards/{reward_id}", response_model=RewardOut)
async def update_reward(family_id: int, reward_id: int, body: RewardUpdate, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.update_reward(db, family_id, actor, reward_id, body.model_dump(exclude_unset=True))


@router.post("/api/families/{family_id}/rewards/{reward_id}/redeem", response_model=RedemptionOut, status_code=status.HTTP_201_CREATED)
async def redeem_reward(family_id: int, reward_id: int, body: RedemptionRequest, actor: FamilyMembership = Depends(get_family_membership), db: AsyncSession = Depends(get_db)):
    return await service.redeem_reward(db, family_id, actor, reward_id, body.idempotency_key)
