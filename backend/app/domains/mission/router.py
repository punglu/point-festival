from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_player, require_admin, require_self_player_id
from app.domains.mission.models import Mission
from app.domains.mission.schema import MissionCreate, MissionUpdate, MissionPropose, MissionResponse
from app.domains.mission.service import (
    get_missions_by_player_date, create_mission, update_mission,
    soft_delete_mission, propose_mission, batch_copy_missions,
    get_missions_by_range,
)
from app.domains.mission_template.service import get_week_remaining_missions

router = APIRouter(prefix="/api/missions", tags=["Mission"])


@router.get("/", response_model=list[MissionResponse])
async def list_missions(
    player_id: int = Query(...),
    target_date: date = Query(..., alias="date"),
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """날짜별 미션 목록 조회. 반복 미션 템플릿 Lazy Init 자동 실행."""
    current_player_id = require_self_player_id(user, player_id)
    from app.domains.mission_template.service import generate_missions_from_templates
    generated = await generate_missions_from_templates(db, target_date)
    if generated > 0:
        await db.commit()
    return await get_missions_by_player_date(db, current_player_id, target_date)


@router.post("/", response_model=MissionResponse, status_code=201)
async def add_mission(
    data: MissionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """Legacy direct creation is retained only for an administrator."""
    return await create_mission(db, data)


@router.patch("/{mission_id}", response_model=MissionResponse)
async def edit_mission(
    mission_id: int,
    data: MissionUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_player),
):
    """미션 수정 (상태 변경 포함). JWT role 기반 권한 검증"""
    mission = await db.get(Mission, mission_id)
    if not mission or mission.deleted_at is not None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    require_self_player_id(user, mission.player_id)
    return await update_mission(db, mission_id, data, role="player")


@router.delete("/{mission_id}", status_code=204)
async def remove_mission(
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """미션 소프트 삭제"""
    await soft_delete_mission(db, mission_id)


@router.post("/propose", response_model=MissionResponse, status_code=201)
async def submit_proposal(
    data: MissionPropose,
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """아이 미션 제안"""
    current_player_id = require_self_player_id(user, data.player_id)
    proposal = data.model_copy(update={"player_id": current_player_id, "proposed_by": user.get("name")})
    return await propose_mission(db, proposal)


@router.post("/copy", response_model=list[MissionResponse], status_code=201)
async def copy_missions(
    player_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """미션 일괄 복제"""
    return await batch_copy_missions(db, player_id, from_date, to_date)


@router.post("/batch-copy", response_model=list[MissionResponse], status_code=201)
async def batch_copy_missions_alias(
    player_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """미션 일괄 복제 (batch-copy alias)"""
    return await batch_copy_missions(db, player_id, from_date, to_date)


@router.get("/weekly")
async def weekly_missions(
    player_id: int,
    week_start: str,
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """주간 전체 미션 조회 (월~일 7일치). 날짜별 그룹핑하여 반환."""
    from datetime import datetime, timedelta
    current_player_id = require_self_player_id(user, player_id)
    start = datetime.strptime(week_start, "%Y-%m-%d").date()
    end = start + timedelta(days=6)
    return await get_missions_by_range(db, current_player_id, start, end)


@router.get("/weekly-remaining")
async def weekly_remaining(
    player_id: int,
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """이번 주 남은 미션 (status=active) 조회. 월~일 기준."""
    current_player_id = require_self_player_id(user, player_id)
    today = date.today()
    # ISO 기준 월요일 시작
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    missions = await get_week_remaining_missions(db, current_player_id, start_of_week, end_of_week)
    total_points = sum(m["point"] for m in missions)

    # 이번 주 전체 미션 수 (삭제되지 않은, active/completed/pending_approval 포함)
    total_stmt = select(func.count()).where(
        Mission.player_id == current_player_id,
        Mission.date >= start_of_week,
        Mission.date <= end_of_week,
        Mission.deleted_at.is_(None),
    )
    total_count = (await db.execute(total_stmt)).scalar() or 0

    return {
        "start_date": str(start_of_week),
        "end_date": str(end_of_week),
        "total_count": total_count,
        "remaining_count": len(missions),
        "remaining_points": total_points,
        "missions": missions,
    }
