from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.domains.cheer.schema import CheerCreate, CheerResponse
from app.domains.cheer.service import get_cheers_by_date, upsert_cheer

router = APIRouter(prefix="/api/cheers", tags=["Cheer"])


@router.get("/", response_model=list[CheerResponse])
async def list_cheers(
    target_date: date = Query(..., alias="date"),
    _: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 응원 메시지 조회"""
    return await get_cheers_by_date(db, target_date)


@router.post("/", response_model=CheerResponse, status_code=201)
async def save_cheer(
    data: CheerCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """응원 메시지 저장 (Upsert)"""
    return await upsert_cheer(db, data)
