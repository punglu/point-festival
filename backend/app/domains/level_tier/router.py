"""Level Tier 라우터"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_player, require_admin, require_self_player_id
from app.domains.level_tier import service
from app.domains.level_tier.schema import (
    LevelTierResponse,
    LevelTierCreate,
    LevelTierUpdate,
    LevelTierBulkSave,
    PlayerLevelInfo,
)

router = APIRouter(prefix="/api/level-tiers", tags=["level-tiers"])


@router.get("", response_model=list[LevelTierResponse])
async def list_tiers(
    job_code: str = "COMMON",
    _: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 목록 조회 (인증 불필요 — FE ExpBar에서 호출)"""
    return await service.get_tiers_by_job(db, job_code)


@router.get("/player/{player_id}", response_model=PlayerLevelInfo)
async def player_level(
    player_id: int,
    job_code: str = "COMMON",
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """플레이어 현재 레벨 조회 (인증 불필요 — FE ExpBar/Ranking에서 호출)"""
    return await service.get_player_level(db, require_self_player_id(user, player_id), job_code)


@router.post("", response_model=LevelTierResponse, status_code=201)
async def create_tier(
    data: LevelTierCreate,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 추가 (Admin용)"""
    result = await service.create_tier(db, data)
    await db.commit()
    return result


@router.patch("/{tier_id}", response_model=LevelTierResponse)
async def update_tier(
    tier_id: int,
    data: LevelTierUpdate,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 수정 (Admin용)"""
    result = await service.update_tier(db, tier_id, data)
    await db.commit()
    return result


@router.delete("/{tier_id}", status_code=204)
async def delete_tier(
    tier_id: int,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 삭제 (Admin용)"""
    await service.delete_tier(db, tier_id)
    await db.commit()


@router.put("/bulk", response_model=list[LevelTierResponse])
async def bulk_save(
    data: LevelTierBulkSave,
    _: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """레벨 구간 벌크 저장 — 전체 교체 (Admin UI 저장 버튼용)"""
    result = await service.bulk_save_tiers(db, data)
    await db.commit()
    return result
