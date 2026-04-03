from datetime import date, datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.deduction.models import Deduction
from app.domains.deduction.schema import DeductionCreate, DeductionUpdate, DeductionResponse


async def _adjust_daily_point_spent(
    db: AsyncSession, player_id: int, target_date: date, delta: int
) -> None:
    """
    -- [SQL] daily_points spent 조정 (차감 생성/수정/삭제 연동)
    -- SELECT * FROM daily_points WHERE player_id = :pid AND date = :date FOR UPDATE;
    -- 존재: UPDATE SET spent = spent + :delta, balance = earned - (spent + :delta)
    -- 미존재: INSERT (earned=0, spent=:delta, balance=-:delta)
    """
    from app.domains.daily_point.models import DailyPoint

    stmt = (
        select(DailyPoint)
        .where(
            DailyPoint.player_id == player_id,
            DailyPoint.date == target_date,
            DailyPoint.deleted_at.is_(None),
        )
        .with_for_update()
    )
    result = await db.execute(stmt)
    dp = result.scalar_one_or_none()

    if dp:
        dp.spent = dp.spent + delta
        dp.balance = dp.earned - dp.spent
    else:
        dp = DailyPoint(
            player_id=player_id,
            date=target_date,
            earned=0,
            spent=delta,
            balance=-delta,
        )
        db.add(dp)


async def get_deductions_by_player_date(
    db: AsyncSession, player_id: int, target_date: date
) -> list[DeductionResponse]:
    """
    -- [SQL] 플레이어의 날짜별 차감 내역 조회
    -- SELECT * FROM deductions
    -- WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL
    -- ORDER BY id ASC;
    """
    stmt = (
        select(Deduction)
        .where(Deduction.player_id == player_id, Deduction.date == target_date, Deduction.deleted_at.is_(None))
        .order_by(Deduction.id.asc())
    )
    result = await db.execute(stmt)
    return [DeductionResponse.model_validate(r) for r in result.scalars().all()]


async def create_deduction(db: AsyncSession, data: DeductionCreate) -> DeductionResponse:
    """
    -- [SQL] 차감 내역 생성 + daily_points spent 자동 연동
    -- INSERT INTO deductions (player_id, date, reason, amount, created_at) VALUES (..., NOW());
    -- UPDATE daily_points SET spent = spent + :amount, balance = earned - spent
    --   WHERE player_id = :pid AND date = :date;
    """
    deduction = Deduction(**data.model_dump())
    db.add(deduction)
    await db.flush()

    await _adjust_daily_point_spent(db, data.player_id, data.date, data.amount)

    await db.commit()
    await db.refresh(deduction)
    return DeductionResponse.model_validate(deduction)


async def get_deductions_admin(
    db: AsyncSession,
    player_id: Optional[int] = None,
    target_date: Optional[date] = None,
) -> list[DeductionResponse]:
    """
    -- [SQL] Admin 차감 내역 조회 (player_id, date 선택 필터)
    -- SELECT * FROM deductions
    -- WHERE deleted_at IS NULL
    -- [AND player_id = :player_id] [AND date = :date]
    -- ORDER BY id ASC;
    """
    stmt = select(Deduction).where(Deduction.deleted_at.is_(None))
    if player_id is not None:
        stmt = stmt.where(Deduction.player_id == player_id)
    if target_date is not None:
        stmt = stmt.where(Deduction.date == target_date)
    stmt = stmt.order_by(Deduction.id.asc())
    result = await db.execute(stmt)
    return [DeductionResponse.model_validate(d) for d in result.scalars().all()]


async def update_deduction(
    db: AsyncSession, deduction_id: int, data: DeductionUpdate
) -> DeductionResponse:
    """
    -- [SQL] 차감 내역 수정 + amount 변경 시 daily_points spent 자동 연동
    -- SELECT * FROM deductions WHERE id = :id AND deleted_at IS NULL;
    -- UPDATE deductions SET reason = :reason, amount = :amount, updated_at = NOW()
    -- WHERE id = :id;
    -- (금액 변경 시) daily_points spent 자동 조정
    """
    stmt = select(Deduction).where(Deduction.id == deduction_id, Deduction.deleted_at.is_(None))
    result = await db.execute(stmt)
    deduction = result.scalar_one_or_none()
    if not deduction:
        raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")

    old_amount = deduction.amount
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(deduction, key, value)

    # 금액 변경 시 daily_points spent 자동 조정
    if "amount" in update_data and update_data["amount"] != old_amount:
        from app.domains.daily_point.service import adjust_daily_point
        from app.domains.daily_point.schema import DailyPointAdjust

        spent_delta = update_data["amount"] - old_amount
        await adjust_daily_point(db, DailyPointAdjust(
            player_id=deduction.player_id,
            date=deduction.date,
            earned_delta=0,
            spent_delta=spent_delta,
        ))

    await db.commit()
    await db.refresh(deduction)
    return DeductionResponse.model_validate(deduction)


async def soft_delete_deduction(db: AsyncSession, deduction_id: int) -> None:
    """
    -- [SQL] 차감 소프트 삭제 + daily_points spent 원복
    -- UPDATE deductions SET deleted_at = NOW() WHERE id = :id AND deleted_at IS NULL;
    -- UPDATE daily_points SET spent = spent - :amount, balance = earned - spent
    --   WHERE player_id = :pid AND date = :date;
    """
    stmt = select(Deduction).where(Deduction.id == deduction_id, Deduction.deleted_at.is_(None))
    result = await db.execute(stmt)
    deduction = result.scalar_one_or_none()
    if not deduction:
        raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")

    deduction.deleted_at = datetime.now(timezone.utc)
    await db.flush()

    await _adjust_daily_point_spent(db, deduction.player_id, deduction.date, -deduction.amount)

    await db.commit()
