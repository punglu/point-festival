from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.deduction.schema import DeductionCreate, DeductionUpdate, DeductionResponse
from app.domains.deduction.service import (
    get_deductions_by_player_date, create_deduction, update_deduction, soft_delete_deduction
)

router = APIRouter(prefix="/api/deductions", tags=["Deduction"])


@router.get("/", response_model=list[DeductionResponse])
async def list_deductions(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 차감 내역 조회"""
    return await get_deductions_by_player_date(db, player_id, target_date)


@router.post("/", response_model=DeductionResponse, status_code=201)
async def add_deduction(data: DeductionCreate, db: AsyncSession = Depends(get_db)):
    """차감 내역 추가"""
    return await create_deduction(db, data)


@router.patch("/{deduction_id}", response_model=DeductionResponse)
async def edit_deduction(
    deduction_id: int,
    data: DeductionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """차감 내역 수정"""
    return await update_deduction(db, deduction_id, data)


@router.delete("/{deduction_id}", status_code=204)
async def remove_deduction(deduction_id: int, db: AsyncSession = Depends(get_db)):
    """차감 소프트 삭제"""
    await soft_delete_deduction(db, deduction_id)
