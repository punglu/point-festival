from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.deduction.models import Deduction
from app.domains.deduction.schema import DeductionCreate, DeductionResponse


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
    -- [SQL] 차감 내역 생성
    -- INSERT INTO deductions (player_id, date, reason, amount, created_at) VALUES (..., NOW());
    """
    deduction = Deduction(**data.model_dump())
    db.add(deduction)
    await db.commit()
    await db.refresh(deduction)
    return DeductionResponse.model_validate(deduction)


async def soft_delete_deduction(db: AsyncSession, deduction_id: int) -> None:
    """
    -- [SQL] 차감 소프트 삭제
    -- UPDATE deductions SET deleted_at = NOW() WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Deduction).where(Deduction.id == deduction_id, Deduction.deleted_at.is_(None))
    result = await db.execute(stmt)
    deduction = result.scalar_one_or_none()
    if not deduction:
        raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")
    deduction.deleted_at = datetime.now(timezone.utc)
    await db.commit()
