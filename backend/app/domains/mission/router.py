from datetime import date

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.mission.schema import MissionCreate, MissionUpdate, MissionPropose, MissionResponse
from app.domains.mission.service import (
    get_missions_by_player_date, create_mission, update_mission,
    soft_delete_mission, propose_mission, batch_copy_missions,
)

router = APIRouter(prefix="/api/missions", tags=["Mission"])


@router.get("/", response_model=list[MissionResponse])
async def list_missions(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 미션 목록 조회"""
    return await get_missions_by_player_date(db, player_id, target_date)


@router.post("/", response_model=MissionResponse, status_code=201)
async def add_mission(data: MissionCreate, db: AsyncSession = Depends(get_db)):
    """미션 추가"""
    return await create_mission(db, data)


@router.patch("/{mission_id}", response_model=MissionResponse)
async def edit_mission(
    mission_id: int,
    data: MissionUpdate,
    db: AsyncSession = Depends(get_db),
    x_player_role: str = Header(default="player", alias="X-Player-Role"),
):
    """미션 수정 (상태 변경 포함). X-Player-Role 헤더로 역할 전달 — Phase 4 JWT로 대체 예정"""
    return await update_mission(db, mission_id, data, role=x_player_role)


@router.delete("/{mission_id}", status_code=204)
async def remove_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    """미션 소프트 삭제"""
    await soft_delete_mission(db, mission_id)


@router.post("/propose", response_model=MissionResponse, status_code=201)
async def submit_proposal(data: MissionPropose, db: AsyncSession = Depends(get_db)):
    """아이 미션 제안"""
    return await propose_mission(db, data)


@router.post("/copy", response_model=list[MissionResponse], status_code=201)
async def copy_missions(
    player_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """미션 일괄 복제"""
    return await batch_copy_missions(db, player_id, from_date, to_date)
