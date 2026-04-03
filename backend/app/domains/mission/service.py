from datetime import date, datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.mission.models import Mission
from app.domains.notification.service import emit_notification
from app.domains.mission.schema import (
    MissionCloneRequest, MissionCloneResponse, MissionCloneSelectedRequest,
    MissionCreate, MissionUpdate, MissionPropose, MissionResponse,
)

# 역할별 미션 상태 전환 규칙 (단일 진실 공급원)
ROLE_TRANSITIONS: dict[str, dict[str, list[str]]] = {
    "admin": {
        "active": ["pending_approval", "failed"],
        "pending_approval": ["completed", "rejected", "active"],
        "proposed": ["active", "rejected"],
        "completed": ["cancelled"],   # 관리자만 완료된 미션을 취소 가능
        "failed": ["active"],
        "rejected": [],
        "cancelled": ["active"],      # 취소된 미션을 재활성화 가능 (포인트 재지급은 재완료 시에만)
    },
    "player": {
        "active": ["pending_approval"],
        "proposed": ["active"],
    },
}


async def _get_player_name(db: AsyncSession, player_id: int) -> str:
    """
    -- [SQL] SELECT name FROM players WHERE id = :id AND deleted_at IS NULL;
    """
    from app.domains.player.models import Player
    result = await db.execute(
        select(Player.name).where(Player.id == player_id, Player.deleted_at.is_(None))
    )
    return result.scalar_one_or_none() or "?"


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


async def get_missions_admin(
    db: AsyncSession,
    player_id: Optional[int] = None,
    target_date: Optional[date] = None,
) -> list[MissionResponse]:
    """
    -- [SQL] Admin 미션 조회 (player_id, date 선택 필터)
    -- SELECT * FROM missions
    -- WHERE deleted_at IS NULL
    -- [AND player_id = :player_id] [AND date = :date]
    -- ORDER BY player_id ASC, sort_order ASC, id ASC;
    """
    stmt = select(Mission).where(Mission.deleted_at.is_(None))
    if player_id is not None:
        stmt = stmt.where(Mission.player_id == player_id)
    if target_date is not None:
        stmt = stmt.where(Mission.date == target_date)
    stmt = stmt.order_by(Mission.player_id.asc(), Mission.sort_order.asc(), Mission.id.asc())
    result = await db.execute(stmt)
    return [MissionResponse.model_validate(m) for m in result.scalars().all()]


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


async def _sync_daily_point_on_status_change(
    db: AsyncSession,
    mission: Mission,
    old_status: str,
    new_status: str,
) -> None:
    """미션 상태 변경에 따른 daily_points 자동 동기화 (내부 전용)

    -- [SQL] earned_delta 계산 후 daily_points 증감
    -- completed 진입: earned += mission.point
    -- completed 이탈(→cancelled): earned -= mission.point
    """
    from app.domains.daily_point.service import adjust_daily_point
    from app.domains.daily_point.schema import DailyPointAdjust

    earned_delta = 0

    if new_status == "completed" and old_status != "completed":
        earned_delta = mission.point
    elif old_status == "completed" and new_status != "completed":
        earned_delta = -mission.point

    if earned_delta != 0:
        await adjust_daily_point(db, DailyPointAdjust(
            player_id=mission.player_id,
            date=mission.date,
            earned_delta=earned_delta,
            spent_delta=0,
        ))


async def update_mission(
    db: AsyncSession, mission_id: int, data: MissionUpdate, role: str = "player"
) -> MissionResponse:
    """
    -- [SQL] 미션 수정 (role: 'player'|'admin' — admin만 completed/cancelled 전환 가능)
    -- UPDATE missions SET text = :text, point = :point, status = :status, ...
    -- WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Mission).where(Mission.id == mission_id, Mission.deleted_at.is_(None))
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")

    old_status = mission.status
    updates = data.model_dump(exclude_unset=True)

    if "status" in updates:
        _validate_status_transition(mission.status, updates["status"], role)

    new_status = updates.get("status", old_status)

    for key, value in updates.items():
        setattr(mission, key, value)

    # 포인트 동기화: 상태가 실제 변경된 경우에만
    if "status" in updates and new_status != old_status:
        await _sync_daily_point_on_status_change(db, mission, old_status, new_status)

    # 알림 엔진: 승인 요청 시
    if new_status == "pending_approval" and old_status != "pending_approval":
        name = await _get_player_name(db, mission.player_id)
        await emit_notification(
            db, "approval_request", mission.player_id,
            f"{name}가 \"{mission.text}\" 승인을 요청했어요",
            f"+{mission.point} pt",
        )

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
    await db.flush()

    # 알림 엔진: 미션 제안 시
    await emit_notification(
        db, "proposal", data.player_id,
        f"{data.proposed_by}가 새 미션을 제안했어요: \"{data.text}\"",
        f"+{data.point} pt",
    )

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


async def expire_overdue_missions(db: AsyncSession) -> int:
    """서버 시작 시 마감 경과 미션 일괄 실패 처리

    -- [SQL] UPDATE missions SET status = 'failed', updated_at = NOW()
    -- WHERE status IN ('active', 'pending_approval')
    --   AND date < CURRENT_DATE AND deleted_at IS NULL;
    """
    from datetime import date as date_type
    from sqlalchemy import update as sa_update

    today = date_type.today()
    stmt = (
        sa_update(Mission)
        .where(
            Mission.status.in_(["active", "pending_approval"]),
            Mission.date < today,
            Mission.deleted_at.is_(None),
        )
        .values(status="failed")
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def clone_selected_missions(
    db: AsyncSession, data: MissionCloneSelectedRequest
) -> list[MissionResponse]:
    """
    -- [SQL] 선택된 미션을 대상 날짜로 복제 (단일 트랜잭션)
    -- SELECT * FROM missions
    --   WHERE id IN (:mission_ids) AND deleted_at IS NULL;
    -- 검증: len(results) == len(mission_ids), 불일치 시 400
    -- SELECT COALESCE(MAX(sort_order), -1) + 1 FROM missions
    --   WHERE player_id = :player_id AND date = :target_date AND deleted_at IS NULL;
    -- INSERT INTO missions (player_id, date, text, point, sender, status, sort_order, created_at)
    --   VALUES (:pid, :target_date, :text, :point, :sender, 'active', :next_order, NOW())
    --   FOR EACH selected mission;
    -- COMMIT (전체 성공) or ROLLBACK (전체 실패)
    """
    # 1. 원본 미션 조회
    stmt = select(Mission).where(
        Mission.id.in_(data.mission_ids),
        Mission.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    sources = result.scalars().all()

    if len(sources) != len(data.mission_ids):
        found_ids = {m.id for m in sources}
        missing = [mid for mid in data.mission_ids if mid not in found_ids]
        raise HTTPException(
            status_code=400,
            detail=f"미션을 찾을 수 없습니다: {missing}"
        )

    # 2. 대상 날짜의 현재 최대 sort_order 조회
    max_order_stmt = select(func.coalesce(func.max(Mission.sort_order), -1)).where(
        Mission.player_id == data.player_id,
        Mission.date == data.target_date,
        Mission.deleted_at.is_(None)
    )
    max_order_result = await db.execute(max_order_stmt)
    next_order = max_order_result.scalar() + 1

    # 3. 복제 생성 (status='active' 초기화)
    cloned = []
    for src in sources:
        new_mission = Mission(
            player_id=data.player_id,
            date=data.target_date,
            text=src.text,
            point=src.point,
            sender=src.sender,
            status="active",
            proposed_by="admin_copy",
            sort_order=next_order,
        )
        db.add(new_mission)
        cloned.append(new_mission)
        next_order += 1

    # 4. 단일 커밋 (원자성 보장)
    await db.commit()
    for m in cloned:
        await db.refresh(m)

    return [MissionResponse.model_validate(m) for m in cloned]


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
