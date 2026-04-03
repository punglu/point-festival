from datetime import date, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.daily_point.models import DailyPoint
from app.domains.daily_point.schema import (
    DailyPointUpsert, DailyPointAdjust, DailyPointResponse, PointCycleSummary,
)

KST = ZoneInfo("Asia/Seoul")
VALID_CYCLES = {"daily", "weekly", "monthly", "quarterly", "yearly"}


def get_cycle_date_range(cycle: str, base_date: date) -> tuple[date, date]:
    """
    주기에 따른 시작일~종료일 계산 (KST 기준, sync — DB I/O 없음).

    Args:
        cycle: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly'
        base_date: 기준 날짜

    Returns:
        (start_date, end_date) 튜플
    """
    if cycle not in VALID_CYCLES:
        raise ValueError(f"유효하지 않은 주기: '{cycle}'. 허용값: {VALID_CYCLES}")

    if cycle == "daily":
        return (base_date, base_date)

    elif cycle == "weekly":
        # ISO-8601: 월요일 시작 (weekday()=0)
        start = base_date - timedelta(days=base_date.weekday())
        end = start + timedelta(days=6)
        return (start, end)

    elif cycle == "monthly":
        start = base_date.replace(day=1)
        if start.month == 12:
            end = date(start.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(start.year, start.month + 1, 1) - timedelta(days=1)
        return (start, end)

    elif cycle == "quarterly":
        quarter_start_month = ((base_date.month - 1) // 3) * 3 + 1
        start = date(base_date.year, quarter_start_month, 1)
        if quarter_start_month + 3 > 12:
            end = date(base_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(base_date.year, quarter_start_month + 3, 1) - timedelta(days=1)
        return (start, end)

    else:  # yearly
        return (date(base_date.year, 1, 1), date(base_date.year, 12, 31))


def _get_cycle_label(cycle: str, start: date, end: date) -> str:
    """UI 표시용 라벨 생성 (sync — 순수 계산)"""
    if cycle == "daily":
        return f"{start.strftime('%m/%d')} 포인트"
    elif cycle == "weekly":
        return f"이번 주 ({start.strftime('%m/%d')}~{end.strftime('%m/%d')})"
    elif cycle == "monthly":
        return f"{start.month}월 포인트"
    elif cycle == "quarterly":
        quarter = (start.month - 1) // 3 + 1
        return f"Q{quarter} 포인트"
    elif cycle == "yearly":
        return f"{start.year}년 포인트"
    return ""


async def get_point_cycle_summary(
    db: AsyncSession, player_id: int, base_date: date, cycle: str
) -> PointCycleSummary:
    """
    -- [SQL] 주기별 포인트 집계
    -- SELECT
    --   COALESCE(SUM(earned), 0) AS total_earned,
    --   COALESCE(SUM(spent), 0) AS total_spent,
    --   COALESCE(SUM(balance), 0) AS balance,
    --   COUNT(*) AS day_count
    -- FROM daily_points
    -- WHERE player_id = :player_id
    --   AND date BETWEEN :start_date AND :end_date
    --   AND deleted_at IS NULL;
    """
    if cycle not in VALID_CYCLES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 주기: '{cycle}'")

    start_date, end_date = get_cycle_date_range(cycle, base_date)

    stmt = select(
        sa_func.coalesce(sa_func.sum(DailyPoint.earned), 0).label("total_earned"),
        sa_func.coalesce(sa_func.sum(DailyPoint.spent), 0).label("total_spent"),
        sa_func.coalesce(sa_func.sum(DailyPoint.balance), 0).label("balance"),
        sa_func.count().label("day_count"),
    ).where(
        DailyPoint.player_id == player_id,
        DailyPoint.date >= start_date,
        DailyPoint.date <= end_date,
        DailyPoint.deleted_at.is_(None),
    )

    result = await db.execute(stmt)
    row = result.one()

    return PointCycleSummary(
        player_id=player_id,
        cycle=cycle,
        start_date=start_date,
        end_date=end_date,
        total_earned=row.total_earned,
        total_spent=row.total_spent,
        balance=row.balance,
        day_count=row.day_count,
        label=_get_cycle_label(cycle, start_date, end_date),
    )


async def get_daily_points_admin(
    db: AsyncSession,
    player_id: Optional[int] = None,
    target_date: Optional[date] = None,
) -> list[DailyPointResponse]:
    """
    -- [SQL] Admin 일일 포인트 조회 (player_id, date 선택 필터)
    -- SELECT * FROM daily_points WHERE deleted_at IS NULL
    -- [AND player_id = :player_id] [AND date = :date];
    """
    stmt = select(DailyPoint).where(DailyPoint.deleted_at.is_(None))
    if player_id is not None:
        stmt = stmt.where(DailyPoint.player_id == player_id)
    if target_date is not None:
        stmt = stmt.where(DailyPoint.date == target_date)
    result = await db.execute(stmt)
    return [DailyPointResponse.model_validate(dp) for dp in result.scalars().all()]


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
