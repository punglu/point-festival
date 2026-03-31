from datetime import date, datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.mission.models import Mission
from app.domains.mission.schema import (
    MissionCloneRequest, MissionCloneResponse,
    MissionCreate, MissionUpdate, MissionPropose, MissionResponse,
)

# 역할별 미션 상태 전환 규칙 (단일 진실 공급원)
ROLE_TRANSITIONS: dict[str, dict[str, list[str]]] = {
    "admin": {
        "proposed": ["active", "rejected"],
        "active": ["completed", "failed"],
        "pending_approval": ["completed", "rejected", "active"],
        "completed": ["active"],
        "failed": ["active"],
        "rejected": ["active"],
    },
    "player": {
        "active": ["pending_approval"],
        "proposed": ["active"],
    },
}


def _validate_status_transition(current: str, new: str, role: str) -> None:
    """역할 기반 상태 전환 유효성 검증 (sync — DB I/O 없음)"""
    role_map = ROLE_TRANSITIONS.get(role, {})
    allowed = role_map.get(current, [])
    if new in allowed:
        return
    # admin에게는 허용되지만 player에게 금지된 전환 → 403
    admin_allowed = ROLE_TRANSITIONS.get("admin", {}).get(current, [])
    if new in admin_allowed:
        raise HTTPException(
            status_code=403,
            detail=f"'{current}' → '{new}' 전환은 admin만 가능합니다",
        )
    # 어떤 역할도 허용하지 않는 전환 → 400
    raise HTTPException(
        status_code=400,
        detail=f"'{current}' → '{new}' 전환은 허용되지 않습니다",
    )


async def get_missions_by_player_date(
    db: AsyncSession, player_id: int, target_date: date
) -> list[MissionResponse]:
    """
    -- [SQL] 특정 플레이어의 날짜별 미션 목록 조회
    -- SELECT * FROM missions
    -- WHERE player_id = :player_id AND date = :date AND deleted_at IS NULL
    -- ORDER BY sort_order ASC, id ASC;
    """
    stmt = (
        select(Mission)
        .where(Mission.player_id == player_id, Mission.date == target_date, Mission.deleted_at.is_(None))
        .order_by(Mission.sort_order.asc(), Mission.id.asc())
    )
    result = await db.execute(stmt)
    return [MissionResponse.model_validate(r) for r in result.scalars().all()]


async def create_mission(db: AsyncSession, data: MissionCreate) -> MissionResponse:
    """
    -- [SQL] 미션 생성
    -- INSERT INTO missions (player_id, date, text, point, sender, msg, status, sort_order, created_at)
    -- VALUES (:player_id, :date, :text, :point, :sender, :msg, :status, :sort_order, NOW());
    """
    mission = Mission(**data.model_dump())
    db.add(mission)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def update_mission(
    db: AsyncSession, mission_id: int, data: MissionUpdate, role: str = "player"
) -> MissionResponse:
    """
    -- [SQL] 미션 수정 (role: 'player'|'admin' — admin만 completed/failed/rejected 전환 가능)
    -- UPDATE missions SET text = :text, point = :point, status = :status, ...
    -- WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Mission).where(Mission.id == mission_id, Mission.deleted_at.is_(None))
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        _validate_status_transition(mission.status, updates["status"], role)
    for key, value in updates.items():
        setattr(mission, key, value)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def update_mission_status(
    db: AsyncSession, mission_id: int, new_status: str, role: str = "player"
) -> MissionResponse:
    """미션 상태 전용 변경 — 상태 전이 검증은 update_mission 내 _validate_status_transition 위임

    -- [SQL] 미션 상태 변경
    -- UPDATE missions SET status = :status, updated_at = NOW()
    -- WHERE id = :id AND deleted_at IS NULL;
    """
    mission_update = MissionUpdate(status=new_status)
    return await update_mission(db, mission_id, mission_update, role=role)


async def soft_delete_mission(db: AsyncSession, mission_id: int) -> None:
    """
    -- [SQL] 미션 소프트 삭제
    -- UPDATE missions SET deleted_at = NOW() WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Mission).where(Mission.id == mission_id, Mission.deleted_at.is_(None))
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    mission.deleted_at = datetime.now(timezone.utc)
    await db.commit()


async def propose_mission(db: AsyncSession, data: MissionPropose) -> MissionResponse:
    """
    -- [SQL] 아이가 미션 제안
    -- INSERT INTO missions (player_id, date, text, point, status, proposed_by, proposal_reason, ...)
    -- VALUES (:player_id, :date, :text, :point, 'proposed', :proposed_by, :reason, ...);
    """
    mission = Mission(
        **data.model_dump(),
        status="proposed",
    )
    db.add(mission)
    await db.commit()
    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def clone_missions(
    db: AsyncSession,
    request: MissionCloneRequest,
) -> MissionCloneResponse:
    """Admin 전용 — 미션 복제 (포인트 오버라이드 지원)

    -- [SQL] 원본 날짜 미션 조회 후 대상 날짜에 복제
    -- SELECT * FROM missions
    -- WHERE player_id = :source_player_id AND date = :source_date AND deleted_at IS NULL;
    --
    -- for each row:
    -- INSERT INTO missions (player_id, date, text, point, sender, status, sort_order, created_at)
    -- VALUES (:player_id, :target_date, :text, :point_override_or_original, :sender, 'active', :sort_order, NOW());
    """
    source = await get_missions_by_player_date(db, request.source_player_id, request.source_date)
    created = []
    for m in source:
        new_point = m.point
        if request.point_overrides and m.id in request.point_overrides:
            new_point = request.point_overrides[m.id]
        new_mission = Mission(
            player_id=request.source_player_id,
            date=request.target_date,
            text=m.text,
            point=new_point,
            sender=m.sender,
            status="active",
            sort_order=m.sort_order,
        )
        db.add(new_mission)
        created.append(new_mission)
    await db.commit()
    for m in created:
        await db.refresh(m)
    return MissionCloneResponse(
        cloned_count=len(created),
        missions=[MissionResponse.model_validate(m) for m in created],
    )


async def batch_copy_missions(
    db: AsyncSession, player_id: int, from_date: date, to_date: date
) -> list[MissionResponse]:
    """
    -- [SQL] 특정 날짜의 미션을 다른 날짜로 일괄 복제 (Python loop INSERT — 가족 규모 데이터)
    -- SELECT * FROM missions WHERE player_id=:pid AND date=:from_date AND deleted_at IS NULL;
    -- for each row: INSERT INTO missions (player_id, date, text, point, sender, status, sort_order)
    --               VALUES (:player_id, :to_date, :text, :point, :sender, 'active', :sort_order);
    """
    source = await get_missions_by_player_date(db, player_id, from_date)
    created = []
    for m in source:
        new_mission = Mission(
            player_id=player_id, date=to_date, text=m.text, point=m.point,
            sender=m.sender, status="active", sort_order=m.sort_order,
        )
        db.add(new_mission)
        created.append(new_mission)
    await db.commit()
    for m in created:
        await db.refresh(m)
    return [MissionResponse.model_validate(m) for m in created]
