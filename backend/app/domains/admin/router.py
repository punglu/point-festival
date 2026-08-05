"""Admin 전용 집합 라우터.
각 도메인의 기존 서비스를 재사용하되, get_admin_user 의존성으로 Admin 권한을 검증.
비즈니스 로직은 각 도메인의 service.py에 위임 (Thin Controller 원칙).
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.auth.dependencies import get_current_admin

from app.domains.mission.schema import (
    MissionCreate,
    MissionUpdate,
    MissionStatusUpdate,
    MissionCloneRequest,
    MissionCloneResponse,
    MissionCloneSelectedRequest,
    MissionResponse,
)
from app.domains.mission.models import Mission
from app.domains.mission.service import (
    admin_revert_mission,
    clone_selected_missions,
    create_mission,
    expire_stale_missions,
    get_current_cycle,
    get_cycle_range,
    get_missions_admin,
    update_mission,
    update_mission_status,
    soft_delete_mission,
    clone_missions,
    get_missions_by_range,
    bulk_approve_missions,
    get_cycle_mission_progress,
)

from app.domains.deduction.schema import DeductionCreate, DeductionUpdate, DeductionResponse
from app.domains.deduction.service import (
    create_deduction,
    get_deductions_admin,
    update_deduction,
    soft_delete_deduction,
)

from app.domains.daily_point.schema import DailyPointAdjust, DailyPointResponse
from app.domains.daily_point.service import adjust_daily_point, get_daily_points_admin, get_daily_points_range

from app.domains.cheer.schema import CheerCreate, CheerResponse
from app.domains.cheer.service import upsert_cheer

from app.domains.player.schema import PlayerListItem, PlayerLockRequest, PlayerUpdateAdmin, PlayerVisibilityRequest
from app.domains.player.service import lock_player, update_player_admin, get_player_list, change_player_pin, set_player_visibility

from app.domains.login_log.schema import LoginLogResponse
from app.domains.login_log.service import get_all_login_logs

from app.domains.notification.schema import NotificationCreate, NotificationResponse
from app.domains.notification.service import (
    create_notification,
    get_all_notifications,
    get_unread_notifications,
    mark_as_read,
    mark_all_as_read,
)

from app.domains.feedback.schema import FeedbackReplyCreate, FeedbackReplyResponse, FeedbackResponse
from app.domains.feedback.service import get_feedbacks_by_player, add_reply

from app.domains.config.schema import ConfigResponse, ConfigUpdate
from app.domains.config.service import get_all_configs, upsert_config

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ─── 플레이어 목록 ─────────────────────────────────────────
@router.get("/players", response_model=list[PlayerListItem])
async def admin_list_players(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_player_list(db)


# ─── 미션 ────────────────────────────────────────────────
@router.get("/missions", response_model=list[MissionResponse])
async def admin_list_missions(
    player_id: Optional[int] = Query(None),
    target_date: Optional[date] = Query(None, alias="date"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    # Lazy Expiry: 현재 주기 이전 미완료 미션 자동 실패 처리
    current_cycle = await get_current_cycle(db)
    cycle_start, cycle_end = get_cycle_range(current_cycle, date.today())
    expired_count = await expire_stale_missions(db, cycle_start)
    if expired_count > 0:
        await db.commit()
    return await get_missions_admin(db, player_id, target_date, date_from, date_to)


@router.post("/missions", response_model=MissionResponse, status_code=201)
async def admin_create_mission(
    data: MissionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await create_mission(db, data)


@router.patch("/missions/{mission_id}/status", response_model=MissionResponse)
async def update_mission_status_admin(
    mission_id: int,
    status_data: MissionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await update_mission_status(
        db=db, mission_id=mission_id, new_status=status_data.status, role="admin"
    )


@router.patch("/missions/{mission_id}", response_model=MissionResponse)
async def admin_update_mission(
    mission_id: int,
    data: MissionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await update_mission(db, mission_id, data, role="admin")


@router.post("/missions/{mission_id}/revert", response_model=MissionResponse)
async def revert_mission(
    mission_id: int,
    _: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """관리자 전용: 완료 미션을 active로 복구 + 포인트 자동 환수"""
    result = await admin_revert_mission(db, mission_id)
    await db.commit()
    return result


@router.delete("/missions/by-group/{group_id}", status_code=204)
async def admin_delete_missions_by_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """group_id가 같은 미션 전체 소프트 삭제 (모두에게 할당된 미션 일괄 삭제)"""
    from datetime import datetime, timezone
    from sqlalchemy import update as sql_update
    now = datetime.now(timezone.utc)
    await db.execute(
        sql_update(Mission)
        .where(Mission.group_id == group_id, Mission.deleted_at.is_(None))
        .values(deleted_at=now)
    )
    await db.commit()


@router.delete("/missions/{mission_id}", status_code=204)
async def admin_delete_mission(
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    await soft_delete_mission(db, mission_id)


@router.post("/missions/clone", response_model=MissionCloneResponse, status_code=201)
async def admin_clone_missions(
    data: MissionCloneRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await clone_missions(db, data)


@router.post("/missions/clone-selected", response_model=list[MissionResponse], status_code=201)
async def admin_clone_selected_missions(
    data: MissionCloneSelectedRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """선택된 미션을 대상 날짜로 복제 (단일 트랜잭션)"""
    return await clone_selected_missions(db, data)


# ─── 포인트 차감 ─────────────────────────────────────────
@router.get("/deductions", response_model=list[DeductionResponse])
async def admin_list_deductions(
    player_id: Optional[int] = Query(None),
    target_date: Optional[date] = Query(None, alias="date"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_deductions_admin(db, player_id, target_date)


@router.post("/deductions", response_model=DeductionResponse, status_code=201)
async def admin_create_deduction(
    data: DeductionCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await create_deduction(db, data)


@router.patch("/deductions/{deduction_id}", response_model=DeductionResponse)
async def admin_update_deduction(
    deduction_id: int,
    data: DeductionUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await update_deduction(db, deduction_id, data)


@router.delete("/deductions/{deduction_id}", status_code=204)
async def admin_delete_deduction(
    deduction_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    await soft_delete_deduction(db, deduction_id)


# ─── 포인트 동기화 ────────────────────────────────────────
@router.get("/daily-points", response_model=list[DailyPointResponse])
async def admin_list_daily_points(
    player_id: Optional[int] = Query(None),
    target_date: Optional[date] = Query(None, alias="date"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_daily_points_admin(db, player_id, target_date)


# MONGLE-W7-4-ADMIN-DAILY-POINTS-RANGE-ACCESS-CONTRACT-REMEDIATION-001: the
# player-facing `/api/daily-points/range` requires `get_current_player` and
# self-scopes to the caller's own player_id, so it 403s for every Admin
# session (Account-native or legacy alike) regardless of which player_id is
# requested — Admin's balancing view needs an arbitrary player's range, not
# its own. Rather than widen the player route's authorization (which would
# let any Admin token bypass the self-only guarantee that route documents
# for its real audience), this is a separate Admin-scoped route reusing the
# same `get_daily_points_range` query unchanged: same data, same shape,
# authorized by `get_current_admin` instead.
@router.get("/daily-points/range", response_model=list[DailyPointResponse])
async def admin_list_daily_points_range(
    player_id: int = Query(...),
    start_date: date = Query(..., alias="start"),
    end_date: date = Query(..., alias="end"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_daily_points_range(db, player_id, start_date, end_date)


@router.post("/daily-points/adjust", response_model=DailyPointResponse)
async def admin_adjust_daily_point(
    data: DailyPointAdjust,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await adjust_daily_point(db, data)


# ─── 응원 메시지 ──────────────────────────────────────────
@router.put("/cheers/{target_date}", response_model=CheerResponse)
async def admin_upsert_cheer(
    target_date: date,
    data: CheerCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await upsert_cheer(db, data)


# ─── 플레이어 관리 ────────────────────────────────────────
@router.patch("/players/{player_id}", response_model=PlayerListItem)
async def admin_update_player(
    player_id: int,
    data: PlayerUpdateAdmin,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await update_player_admin(db, player_id, data)


@router.patch("/players/{player_id}/pin", status_code=204)
async def admin_change_player_pin(
    player_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    await change_player_pin(db, player_id, data["pin"])


@router.patch("/players/{player_id}/lock", response_model=PlayerListItem)
async def admin_lock_player(
    player_id: int,
    data: PlayerLockRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await lock_player(db, player_id, data)


@router.patch("/players/{player_id}/visibility", response_model=PlayerListItem)
async def admin_set_player_visibility(
    player_id: int,
    data: PlayerVisibilityRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await set_player_visibility(db, player_id, data)


# ─── 알림 ────────────────────────────────────────────────
@router.get("/notifications", response_model=list[NotificationResponse])
async def admin_get_notifications(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_all_notifications(db)


@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def admin_create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await create_notification(db, data)


@router.patch("/notifications/read-all", status_code=204)
async def admin_mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    await mark_all_as_read(db)


@router.patch("/notifications/{notification_id}/read", status_code=204)
async def admin_mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    await mark_as_read(db, notification_id)


# ─── 피드백 ───────────────────────────────────────────────
@router.get("/feedbacks", response_model=list[FeedbackResponse])
async def admin_get_feedbacks(
    player_id: int,
    target_date: date,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_feedbacks_by_player(db, player_id, target_date)


@router.post("/feedbacks/{feedback_id}/replies", response_model=FeedbackReplyResponse, status_code=201)
async def admin_add_reply(
    feedback_id: int,
    data: FeedbackReplyCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await add_reply(db, data)


# ─── 주기 진행률 ──────────────────────────────────────────
@router.get("/cycle-progress")
async def cycle_progress(
    date_from: str,
    date_to: str,
    _: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """주기 범위 전체 플레이어 미션 진행률 (total/completed/rate)"""
    from datetime import datetime as dt_cls
    start = dt_cls.strptime(date_from, "%Y-%m-%d").date()
    end = dt_cls.strptime(date_to, "%Y-%m-%d").date()
    return await get_cycle_mission_progress(db, start, end)


# ─── 주간 요약 ────────────────────────────────────────────
@router.get("/weekly-summary")
async def weekly_summary(
    week_start: str,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin용 주간 요약: 플레이어별 × 요일별 미션 현황"""
    from datetime import datetime, timedelta
    from app.domains.player import service as player_service

    start = datetime.strptime(week_start, "%Y-%m-%d").date()
    end = start + timedelta(days=6)

    players = await player_service.get_player_list(db)
    result = []

    for player in players:
        if player.role != "player":
            continue
        missions = await get_missions_by_range(db, player.id, start, end)

        daily_summary = {}
        for day_offset in range(7):
            d = start + timedelta(days=day_offset)
            d_str = str(d)
            day_missions = missions.get(d_str, [])
            total = len(day_missions)
            done = sum(1 for m in day_missions if m["status"] == "completed")
            points = sum(m["point"] for m in day_missions if m["status"] == "completed")
            pending = sum(1 for m in day_missions if m["status"] == "pending_approval")
            daily_summary[d_str] = {
                "total": total,
                "done": done,
                "points": points,
                "pending": pending,
            }

        result.append({
            "player_id": player.id,
            "player_name": player.name,
            "player_photo": player.photo,
            "daily": daily_summary,
        })

    return {"week_start": week_start, "players": result}


@router.post("/missions/bulk-approve")
async def bulk_approve(
    player_id: int,
    date: str,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """특정 플레이어의 특정 날짜 pending_approval 미션 전체 승인"""
    count = await bulk_approve_missions(db, player_id, date)
    await db.commit()
    return {"approved": count, "player_id": player_id, "date": date}


# ─── 로그인 로그 ──────────────────────────────────────────
@router.get("/login-logs", response_model=list[LoginLogResponse])
async def admin_list_login_logs(
    player_id: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_all_login_logs(db, player_id, limit)


# ─── 설정 ────────────────────────────────────────────────
@router.get("/configs", response_model=list[ConfigResponse])
async def admin_get_configs(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await get_all_configs(db)


@router.put("/configs/{key}", response_model=ConfigResponse)
async def admin_update_config(
    key: str,
    data: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    return await upsert_config(db, key, data)
