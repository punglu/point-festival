import calendar
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.mission.models import Mission
from app.domains.notification.service import emit_notification
from app.domains.mission.schema import (
    MissionCloneRequest, MissionCloneResponse, MissionCloneSelectedRequest,
    MissionCreate, MissionUpdate, MissionPropose, MissionResponse,
)

async def _sync_total_earned(db: AsyncSession, player_id: int, delta: int) -> None:
    """
    -- [SQL] players.total_earned 증감 (ACID 트랜잭션 내에서 호출)
    -- UPDATE players SET total_earned = total_earned + :delta, updated_at = NOW()
    -- WHERE id = :player_id AND deleted_at IS NULL;
    """
    from app.domains.player.models import Player

    stmt = (
        sql_update(Player)
        .where(Player.id == player_id, Player.deleted_at.is_(None))
        .values(
            total_earned=Player.total_earned + delta,
            updated_at=datetime.now(timezone.utc),
        )
    )
    await db.execute(stmt)


def get_week_range(d: date) -> tuple[date, date]:
    """ISO 기준 주간 범위 반환 (월요일 ~ 일요일)"""
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start, end


def is_same_week(d1: date, d2: date) -> bool:
    """두 날짜가 같은 ISO 주차인지 확인"""
    s1, _ = get_week_range(d1)
    s2, _ = get_week_range(d2)
    return s1 == s2


def get_cycle_range(cycle_type: str, ref_date: date) -> tuple[date, date]:
    """
    주기 타입에 따른 시작/종료 날짜 계산.
    지원: daily, weekly, biweekly, monthly, quarterly, yearly
    미지원 값: weekly 폴백
    """
    if cycle_type == "daily":
        return ref_date, ref_date

    elif cycle_type == "weekly":
        start = ref_date - timedelta(days=ref_date.weekday())  # 월요일
        end = start + timedelta(days=6)  # 일요일
        return start, end

    elif cycle_type == "biweekly":
        # ISO week number 기반: 홀수주 시작 → 2주 단위
        start = ref_date - timedelta(days=ref_date.weekday())  # 이번 주 월요일
        iso_week = start.isocalendar()[1]
        if iso_week % 2 == 0:
            start = start - timedelta(weeks=1)  # 홀수주 월요일로 이동
        end = start + timedelta(days=13)  # 2주 뒤 일요일
        return start, end

    elif cycle_type == "monthly":
        start = ref_date.replace(day=1)
        last_day = calendar.monthrange(ref_date.year, ref_date.month)[1]
        end = ref_date.replace(day=last_day)
        return start, end

    elif cycle_type == "quarterly":
        quarter_month = ((ref_date.month - 1) // 3) * 3 + 1  # 1, 4, 7, 10
        start = ref_date.replace(month=quarter_month, day=1)
        end_month = quarter_month + 2
        last_day = calendar.monthrange(ref_date.year, end_month)[1]
        end = ref_date.replace(month=end_month, day=last_day)
        return start, end

    elif cycle_type == "yearly":
        start = ref_date.replace(month=1, day=1)
        end = ref_date.replace(month=12, day=31)
        return start, end

    else:
        # 알 수 없는 주기 → weekly 폴백
        start = ref_date - timedelta(days=ref_date.weekday())
        end = start + timedelta(days=6)
        return start, end


async def get_current_cycle(db: AsyncSession) -> str:
    """
    -- [SQL] 현재 주기 설정 조회
    -- SELECT value FROM app_configs WHERE key = 'point_cycle';
    -- 설계 예외: mission 도메인에서 config 모델 직접 조회 (PM 승인, 읽기 전용 1컬럼)
    """
    from app.domains.config.models import AppConfig
    stmt = select(AppConfig.value).where(AppConfig.key == "point_cycle")
    result = await db.execute(stmt)
    value = result.scalar_one_or_none()
    return value or "weekly"  # 미설정 시 weekly 기본값


async def expire_stale_missions(db: AsyncSession, cycle_start_date: date) -> int:
    """
    -- [SQL] 주기 만료 미션 일괄 실패 처리 (Lazy Expiry)
    -- UPDATE missions
    -- SET status = 'failed',
    --     msg = '[시스템] 주기 마감 자동 실패',
    --     updated_at = NOW()
    -- WHERE date < :cycle_start_date
    --   AND status IN ('active', 'pending_approval')
    --   AND deleted_at IS NULL;
    --
    -- 트리거: Admin 대시보드 미션 조회 시 1회 호출 (Lazy Expiry 패턴)
    -- pending_approval 포함 이유: 주기 내 미승인 = 미완료로 간주
    """
    from sqlalchemy import update as sql_update

    now_utc = datetime.now(timezone.utc)
    stmt = (
        sql_update(Mission)
        .where(
            Mission.date < cycle_start_date,
            Mission.status.in_(["active", "pending_approval"]),
            Mission.deleted_at.is_(None),
        )
        .values(
            status="failed",
            msg="[시스템] 주기 마감 자동 실패",
            updated_at=now_utc,
        )
    )
    result = await db.execute(stmt)
    return result.rowcount


# 역할별 미션 상태 전환 규칙 (단일 진실 공급원)
ROLE_TRANSITIONS: dict[str, dict[str, list[str]]] = {
    "admin": {
        "active": ["pending_approval", "failed", "completed"],
        "pending_approval": ["completed", "rejected", "active"],
        "proposed": ["active", "rejected"],
        "completed": ["cancelled", "active"],  # 관리자만 완료된 미션을 취소/재활성화 가능
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


async def admin_revert_mission(db: AsyncSession, mission_id: int) -> MissionResponse:
    """
    -- [SQL] 관리자 전용: 완료 미션 → active 복구 + 포인트 환수
    --
    -- 1. 미션 조회 (completed + not deleted)
    -- SELECT * FROM missions WHERE id = :id AND status = 'completed' AND deleted_at IS NULL;
    --
    -- 2. 미션 상태 복구
    -- UPDATE missions SET status = 'active', msg = '[시스템] 관리자에 의한 완료 취소'
    -- WHERE id = :id;
    --
    -- 3. 포인트 환수 — adjust_daily_point(earned_delta = -mission.point)
    -- UPDATE daily_points
    -- SET earned = earned - :point, balance = balance - :point
    -- WHERE player_id = :pid AND date = :date AND deleted_at IS NULL;
    """
    from datetime import datetime, timezone
    from app.domains.daily_point.service import adjust_daily_point
    from app.domains.daily_point.schema import DailyPointAdjust

    stmt = select(Mission).where(
        Mission.id == mission_id,
        Mission.status == "completed",
        Mission.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="완료된 미션을 찾을 수 없습니다")

    now_utc = datetime.now(timezone.utc)
    mission.status = "active"
    mission.msg = "[시스템] 관리자에 의한 완료 취소"
    mission.updated_at = now_utc
    await db.flush()

    # 포인트 환수 (earned_delta 음수 → 차감)
    await adjust_daily_point(db, DailyPointAdjust(
        player_id=mission.player_id,
        date=mission.date,
        earned_delta=-mission.point,
        spent_delta=0,
    ))
    await _sync_total_earned(db, mission.player_id, -mission.point)

    await db.refresh(mission)
    return MissionResponse.model_validate(mission)


async def get_missions_admin(
    db: AsyncSession,
    player_id: Optional[int] = None,
    target_date: Optional[date] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[MissionResponse]:
    """
    -- [SQL] Admin 미션 조회 (player_id, date, date_from/date_to 선택 필터)
    -- SELECT * FROM missions
    -- WHERE deleted_at IS NULL
    -- [AND player_id = :player_id]
    -- [AND date = :target_date]
    -- [AND date >= :date_from]
    -- [AND date <= :date_to]
    -- ORDER BY player_id ASC, sort_order ASC, id ASC;
    """
    stmt = select(Mission).where(Mission.deleted_at.is_(None))
    if player_id is not None:
        stmt = stmt.where(Mission.player_id == player_id)
    if target_date is not None:
        stmt = stmt.where(Mission.date == target_date)
    if date_from is not None:
        stmt = stmt.where(Mission.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Mission.date <= date_to)
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
        await _sync_total_earned(db, mission.player_id, earned_delta)


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
        # 주차 검증: player는 이번 주 미션만 상태 변경 가능
        if role == "player" and not is_same_week(date.today(), mission.date):
            raise HTTPException(
                status_code=400,
                detail="이번 주가 아닌 미션은 변경할 수 없습니다.",
            )

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
            f"{mission.date} · +{mission.point}pt",
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
        f"{data.date} · +{data.point}pt",
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
        point = data.point_overrides.get(src.id, src.point) if data.point_overrides else src.point
        new_mission = Mission(
            player_id=data.player_id,
            date=data.target_date,
            text=src.text,
            point=point,
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


async def get_missions_by_range(
    db: AsyncSession, player_id: int, start_date: date, end_date: date
) -> dict:
    """
    -- [SQL] 주간 미션 조회
    -- SELECT * FROM missions
    -- WHERE player_id = :pid AND date BETWEEN :start AND :end
    --   AND deleted_at IS NULL
    -- ORDER BY date ASC, sort_order ASC;
    """
    from collections import defaultdict
    stmt = (
        select(Mission)
        .where(
            Mission.player_id == player_id,
            Mission.date >= start_date,
            Mission.date <= end_date,
            Mission.deleted_at.is_(None),
        )
        .order_by(Mission.date.asc(), Mission.sort_order.asc())
    )
    result = await db.execute(stmt)
    missions = result.scalars().all()

    grouped: dict = defaultdict(list)
    for m in missions:
        grouped[str(m.date)].append({
            "id": m.id,
            "date": str(m.date),
            "text": m.text,
            "point": m.point,
            "status": m.status,
            "sender": m.sender,
            "msg": m.msg,
            "proposed_by": m.proposed_by,
            "created_at": str(m.created_at) if m.created_at else None,
        })
    return dict(grouped)


async def bulk_approve_missions(db: AsyncSession, player_id: int, date_str: str) -> int:
    """
    -- [SQL] 일괄 승인 + total_earned 동기화
    -- SELECT SUM(point) FROM missions
    --   WHERE player_id = :pid AND date = :date AND status = 'pending_approval' AND deleted_at IS NULL;
    -- UPDATE missions SET status = 'completed', updated_at = NOW()
    --   WHERE player_id = :pid AND date = :date AND status = 'pending_approval' AND deleted_at IS NULL;
    -- UPDATE players SET total_earned = total_earned + :sum_points WHERE id = :pid;
    """
    from sqlalchemy import func as sql_func
    from datetime import datetime as dt_class

    target_date = dt_class.strptime(date_str, "%Y-%m-%d").date()

    # 1) 승인 대상 포인트 합계 조회
    sum_stmt = select(sql_func.coalesce(sql_func.sum(Mission.point), 0)).where(
        Mission.player_id == player_id,
        Mission.date == target_date,
        Mission.status == "pending_approval",
        Mission.deleted_at.is_(None),
    )
    sum_result = await db.execute(sum_stmt)
    total_points = int(sum_result.scalar())

    # 2) 일괄 상태 변경
    stmt = (
        sql_update(Mission)
        .where(
            Mission.player_id == player_id,
            Mission.date == target_date,
            Mission.status == "pending_approval",
            Mission.deleted_at.is_(None),
        )
        .values(status="completed", updated_at=datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)

    # 3) total_earned 동기화
    if total_points > 0:
        await _sync_total_earned(db, player_id, total_points)

    return result.rowcount


async def get_cycle_mission_progress(db: AsyncSession, date_from: date, date_to: date) -> dict:
    """주기 범위 전체 플레이어 미션 진행률 집계

    -- [SQL] 주기 내 미션 총 건수 + 완료 건수
    -- SELECT
    --     COUNT(*) as total,
    --     COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
    -- FROM missions
    -- WHERE date BETWEEN :date_from AND :date_to
    --   AND deleted_at IS NULL;
    -- 진행률 = ROUND(completed / total * 100, 1)  (total=0 → 0.0)
    """
    from sqlalchemy import case as sa_case

    stmt = select(
        func.count().label("total"),
        func.count(
            sa_case((Mission.status == "completed", 1))
        ).label("completed"),
    ).where(
        Mission.date >= date_from,
        Mission.date <= date_to,
        Mission.deleted_at.is_(None),
    )

    result = await db.execute(stmt)
    row = result.first()

    total = row.total if row else 0
    completed = row.completed if row else 0
    rate = round(completed / total * 100, 1) if total > 0 else 0.0

    return {
        "total": total,
        "completed": completed,
        "rate": rate,
        "date_from": str(date_from),
        "date_to": str(date_to),
    }
