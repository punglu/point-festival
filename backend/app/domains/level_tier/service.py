"""Level Tier 서비스"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from fastapi import HTTPException

from app.domains.level_tier.models import LevelTier
from app.domains.level_tier.schema import (
    LevelTierResponse,
    LevelTierCreate,
    LevelTierUpdate,
    LevelTierBulkSave,
    PlayerLevelInfo,
)


async def get_tiers_by_job(db: AsyncSession, job_code: str = "COMMON") -> list[LevelTierResponse]:
    """
    -- [SQL] 직업별 레벨 구간 전체 조회
    -- SELECT * FROM level_tiers
    -- WHERE job_code = :job_code
    -- ORDER BY level ASC;
    """
    stmt = (
        select(LevelTier)
        .where(LevelTier.job_code == job_code)
        .order_by(LevelTier.level.asc())
    )
    result = await db.execute(stmt)
    return [LevelTierResponse.model_validate(t) for t in result.scalars().all()]


async def create_tier(db: AsyncSession, data: LevelTierCreate) -> LevelTierResponse:
    """
    -- [SQL] 레벨 구간 추가
    -- INSERT INTO level_tiers (job_code, level, title, required_points, ...)
    -- VALUES (:job_code, :level, :title, :required_points, ...);
    """
    tier = LevelTier(**data.model_dump())
    db.add(tier)
    await db.flush()
    await db.refresh(tier)
    return LevelTierResponse.model_validate(tier)


async def update_tier(db: AsyncSession, tier_id: int, data: LevelTierUpdate) -> LevelTierResponse:
    """
    -- [SQL] 레벨 구간 수정
    -- UPDATE level_tiers SET title = :title, required_points = :points, ...
    -- WHERE id = :id;
    """
    stmt = select(LevelTier).where(LevelTier.id == tier_id)
    result = await db.execute(stmt)
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="레벨 구간을 찾을 수 없습니다")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tier, key, value)
    await db.flush()
    await db.refresh(tier)
    return LevelTierResponse.model_validate(tier)


async def delete_tier(db: AsyncSession, tier_id: int) -> None:
    """
    -- [SQL] 레벨 구간 삭제 (물리 삭제 — Soft Delete 미적용, 설정 데이터)
    -- DELETE FROM level_tiers WHERE id = :id;
    """
    stmt = select(LevelTier).where(LevelTier.id == tier_id)
    result = await db.execute(stmt)
    tier = result.scalar_one_or_none()
    if not tier:
        raise HTTPException(status_code=404, detail="레벨 구간을 찾을 수 없습니다")
    await db.delete(tier)
    await db.flush()


async def bulk_save_tiers(db: AsyncSession, data: LevelTierBulkSave) -> list[LevelTierResponse]:
    """
    -- [SQL] 레벨 구간 벌크 저장 (기존 전체 삭제 후 재생성)
    -- DELETE FROM level_tiers WHERE job_code = :job_code;
    -- INSERT INTO level_tiers (...) VALUES (...), ...;
    """
    sorted_tiers = sorted(data.tiers, key=lambda t: t.required_points)
    for i, tier in enumerate(sorted_tiers):
        if tier.level != i + 1:
            sorted_tiers[i] = tier.model_copy(update={"level": i + 1})

    points_set: set[int] = set()
    for tier in sorted_tiers:
        if tier.required_points in points_set:
            raise HTTPException(status_code=400, detail=f"중복된 포인트 값: {tier.required_points}")
        points_set.add(tier.required_points)

    if sorted_tiers and sorted_tiers[0].required_points != 0:
        raise HTTPException(status_code=400, detail="Lv.1의 필요 포인트는 반드시 0이어야 합니다")

    del_stmt = sql_delete(LevelTier).where(LevelTier.job_code == data.job_code)
    await db.execute(del_stmt)

    new_tiers = []
    for tier_data in sorted_tiers:
        tier = LevelTier(
            job_code=data.job_code,
            level=tier_data.level,
            title=tier_data.title,
            required_points=tier_data.required_points,
            icon_path=tier_data.icon_path,
            milestone_type=tier_data.milestone_type,
            milestone_data=tier_data.milestone_data,
        )
        db.add(tier)
        new_tiers.append(tier)

    await db.flush()
    for t in new_tiers:
        await db.refresh(t)
    return [LevelTierResponse.model_validate(t) for t in new_tiers]


def calculate_level(total_earned: int, tiers: list[LevelTierResponse]) -> PlayerLevelInfo:
    """
    플레이어의 누적 포인트로 레벨 계산.
    정의된 구간 초과 시 하이브리드 자동 확장 (마지막 두 구간의 간격 반복).
    DB 접근 없음 — 순수 계산 함수.
    """
    if not tiers:
        return PlayerLevelInfo(
            player_id=0, total_earned=total_earned,
            level=1, title="Lv.1", current_threshold=0,
            next_threshold=100, progress_percent=0,
        )

    sorted_tiers = sorted(tiers, key=lambda t: t.required_points)

    current_tier = sorted_tiers[0]
    for tier in sorted_tiers:
        if total_earned >= tier.required_points:
            current_tier = tier
        else:
            break

    current_idx = sorted_tiers.index(current_tier)

    if current_idx + 1 < len(sorted_tiers):
        next_threshold = sorted_tiers[current_idx + 1].required_points
        level = current_tier.level
        title = current_tier.title
    else:
        if len(sorted_tiers) >= 2:
            last_gap = sorted_tiers[-1].required_points - sorted_tiers[-2].required_points
        else:
            last_gap = 100
        if last_gap <= 0:
            last_gap = 100
        excess = total_earned - sorted_tiers[-1].required_points

        if excess == 0:
            # 정확히 마지막 정의 구간에 도달 — 정의된 title 사용
            level = current_tier.level
            title = current_tier.title
            next_threshold = current_tier.required_points + last_gap
        else:
            # 초과 — 자동 확장
            extra_levels = excess // last_gap
            level = sorted_tiers[-1].level + extra_levels
            title = f"Lv.{level} (자동)"
            current_threshold_calc = sorted_tiers[-1].required_points + (extra_levels * last_gap)
            next_threshold = current_threshold_calc + last_gap

    current_threshold = current_tier.required_points
    if current_idx + 1 >= len(sorted_tiers) and len(sorted_tiers) >= 2:
        last_gap = sorted_tiers[-1].required_points - sorted_tiers[-2].required_points
        if last_gap <= 0:
            last_gap = 100
        excess = total_earned - sorted_tiers[-1].required_points
        extra_levels = excess // last_gap
        current_threshold = sorted_tiers[-1].required_points + (extra_levels * last_gap)

    range_size = next_threshold - current_threshold
    if range_size > 0:
        progress = int(((total_earned - current_threshold) / range_size) * 100)
        progress = max(0, min(100, progress))
    else:
        progress = 100

    return PlayerLevelInfo(
        player_id=0,
        total_earned=total_earned,
        level=level,
        title=title,
        current_threshold=current_threshold,
        next_threshold=next_threshold,
        progress_percent=progress,
    )


async def get_player_level(db: AsyncSession, player_id: int, job_code: str = "COMMON") -> PlayerLevelInfo:
    """
    -- [SQL] 플레이어 레벨 조회
    -- SELECT total_earned FROM players WHERE id = :pid AND deleted_at IS NULL;
    -- SELECT * FROM level_tiers WHERE job_code = :job_code ORDER BY level ASC;
    """
    from app.domains.player.models import Player

    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")

    tiers = await get_tiers_by_job(db, job_code)
    level_info = calculate_level(player.total_earned, tiers)
    level_info.player_id = player_id
    return level_info
