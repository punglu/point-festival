from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.daily_point.schema import DailyPointAdjust, DailyPointResponse
from app.domains.daily_point.service import get_daily_point, get_daily_points_range, adjust_daily_point

router = APIRouter(prefix="/api/daily-points", tags=["DailyPoint"])


@router.get("/", response_model=Optional[DailyPointResponse])
async def get_point(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """특정 날짜 일일 포인트 조회"""
    return await get_daily_point(db, player_id, target_date)


@router.get("/range", response_model=list[DailyPointResponse])
async def get_points_range(
    player_id: int = Query(...),
    start_date: date = Query(..., alias="start"),
    end_date: date = Query(..., alias="end"),
    db: AsyncSession = Depends(get_db),
):
    """날짜 범위 포인트 조회"""
    return await get_daily_points_range(db, player_id, start_date, end_date)


@router.post("/", response_model=DailyPointResponse, status_code=201)
async def save_point(data: DailyPointAdjust, db: AsyncSession = Depends(get_db)):
    """일일 포인트 델타 조정 (행 잠금)"""
    return await adjust_daily_point(db, data)
