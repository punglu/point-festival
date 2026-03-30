from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.daily_point.models import DailyPoint
from app.domains.daily_point.schema import DailyPointUpsert, DailyPointAdjust, DailyPointResponse


async def get_daily_point(
    db: AsyncSession, player_id: int, target_date: date
) -> Optional[DailyPointResponse]:
    """
    -- [SQL] 특정 날짜의 일일 포인트 조회
    -- SELECT * FROM daily_points
    -- WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL;
    """
    stmt = select(DailyPoint).where(
        DailyPoint.player_id == player_id,
        DailyPoint.date == target_date,
        DailyPoint.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    dp = result.scalar_one_or_none()
    return DailyPointResponse.model_validate(dp) if dp else None


async def get_daily_points_range(
    db: AsyncSession, player_id: int, start_date: date, end_date: date
) -> list[DailyPointResponse]:
    """
    -- [SQL] 날짜 범위 일일 포인트 조회 (랭킹/합산용)
    -- SELECT * FROM daily_points
    -- WHERE player_id = :player_id AND date BETWEEN :start AND :end AND deleted_at IS NULL
    -- ORDER BY date ASC;
    """
    stmt = (
        select(DailyPoint)
        .where(
            DailyPoint.player_id == player_id,
            DailyPoint.date >= start_date,
            DailyPoint.date <= end_date,
            DailyPoint.deleted_at.is_(None),
        )
        .order_by(DailyPoint.date.asc())
    )
    result = await db.execute(stmt)
    return [DailyPointResponse.model_validate(r) for r in result.scalars().all()]


async def upsert_daily_point(db: AsyncSession, data: DailyPointUpsert) -> DailyPointResponse:
    """
    -- [SQL] 일일 포인트 Upsert
    -- SELECT * FROM daily_points WHERE player_id = :pid AND date = :date AND deleted_at IS NULL;
    -- 존재: UPDATE daily_points SET earned=:e, spent=:s, balance=:b WHERE id = :id;
    -- 미존재: INSERT INTO daily_points (player_id, date, earned, spent, balance) VALUES (...);
    """
    stmt = select(DailyPoint).where(
        DailyPoint.player_id == data.player_id,
        DailyPoint.date == data.date,
        DailyPoint.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.earned = data.earned
        existing.spent = data.spent
        existing.balance = data.balance
        await db.commit()
        await db.refresh(existing)
        return DailyPointResponse.model_validate(existing)
    else:
        dp = DailyPoint(**data.model_dump())
        db.add(dp)
        await db.commit()
        await db.refresh(dp)
        return DailyPointResponse.model_validate(dp)


async def adjust_daily_point(db: AsyncSession, data: DailyPointAdjust) -> DailyPointResponse:
    """
    -- [SQL] 델타 기반 포인트 조정 (행 잠금으로 동시성 보호)
    -- SELECT * FROM daily_points
    -- WHERE player_id = :pid AND date = :date AND deleted_at IS NULL
    -- FOR UPDATE;
    -- 존재: UPDATE daily_points
    --       SET earned = earned + :earned_delta,
    --           spent  = spent  + :spent_delta,
    --           balance = balance + :earned_delta - :spent_delta
    --       WHERE id = :id;
    -- 미존재: INSERT INTO daily_points (player_id, date, earned, spent, balance)
    --         VALUES (:pid, :date, :earned_delta, :spent_delta, :earned_delta - :spent_delta);
    """
    stmt = (
        select(DailyPoint)
        .where(
            DailyPoint.player_id == data.player_id,
            DailyPoint.date == data.date,
            DailyPoint.deleted_at.is_(None),
        )
        .with_for_update()
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.earned += data.earned_delta
        existing.spent += data.spent_delta
        existing.balance += data.earned_delta - data.spent_delta
        await db.commit()
        await db.refresh(existing)
        return DailyPointResponse.model_validate(existing)
    else:
        dp = DailyPoint(
            player_id=data.player_id,
            date=data.date,
            earned=data.earned_delta,
            spent=data.spent_delta,
            balance=data.earned_delta - data.spent_delta,
        )
        db.add(dp)
        await db.commit()
        await db.refresh(dp)
        return DailyPointResponse.model_validate(dp)
