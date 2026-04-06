"""미션 템플릿 서비스 — CRUD + Lazy Init 자동 생성"""
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update as sql_update
from fastapi import HTTPException

from app.domains.mission_template.models import MissionTemplate
from app.domains.mission.models import Mission
from app.domains.mission_template.schema import (
    MissionTemplateCreate,
    MissionTemplateUpdate,
    MissionTemplateResponse,
)


# ── 요일 비트마스크 유틸 ──
# 월=1, 화=2, 수=4, 목=8, 금=16, 토=32, 일=64
DAY_BITS = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 32, 6: 64}  # Python weekday → bit


def matches_day(bitmask: int, target_date: date) -> bool:
    """주어진 날짜가 bitmask 요일에 해당하는지 확인"""
    weekday = target_date.weekday()  # 0=월 ~ 6=일
    return bool(bitmask & DAY_BITS.get(weekday, 0))


async def list_templates(db: AsyncSession, player_id: int | None = None) -> list[MissionTemplateResponse]:
    """
    -- [SQL] 템플릿 목록 조회
    -- SELECT * FROM mission_templates WHERE deleted_at IS NULL
    --   [AND player_id = :player_id] ORDER BY created_at DESC;
    """
    stmt = select(MissionTemplate).where(MissionTemplate.deleted_at.is_(None))
    if player_id:
        stmt = stmt.where(MissionTemplate.player_id == player_id)
    stmt = stmt.order_by(MissionTemplate.created_at.desc())
    result = await db.execute(stmt)
    return [MissionTemplateResponse.model_validate(t) for t in result.scalars().all()]


def get_rolling_window() -> tuple[date, date]:
    """
    롤링 윈도우 범위: 오늘 ~ 다음 주 일요일
    예) 오늘이 토요일(4/4)이면 → 4/4(토) ~ 4/12(일) = 9일간
    예) 오늘이 월요일(3/30)이면 → 3/30(월) ~ 4/5(일) = 7일간 (이번 주만)
    """
    from datetime import timedelta
    today = date.today()
    days_until_sunday = 6 - today.weekday()  # weekday(): 0=월 ~ 6=일
    this_sunday = today + timedelta(days=days_until_sunday)
    next_sunday = this_sunday + timedelta(days=7)
    return today, next_sunday


async def generate_missions_for_range(
    db: AsyncSession, start_date: date, end_date: date
) -> int:
    """
    -- [SQL] 롤링 윈도우: 지정 범위의 각 날짜에 대해 템플릿 미션 일괄 생성
    -- FOR each date IN [start_date .. end_date]:
    --   기존 generate_missions_from_templates(db, date) 호출
    --   → 중복 방지 로직(player_id, date, text, point 조합)이 이미 내장됨
    --   → 이미 존재하는 미션은 스킵, 새로운 것만 INSERT
    """
    from datetime import timedelta
    total_created = 0
    current = start_date
    while current <= end_date:
        count = await generate_missions_from_templates(db, current)
        total_created += count
        current += timedelta(days=1)
    await db.flush()
    return total_created


async def create_template(db: AsyncSession, data: MissionTemplateCreate) -> MissionTemplateResponse:
    """
    -- [SQL] 템플릿 생성
    -- INSERT INTO mission_templates (player_id, text, point, day_of_week)
    -- VALUES (:player_id, :text, :point, :day_of_week);
    --
    -- 생성 후: 롤링 윈도우(오늘~다음주 일요일) 범위 미션 즉시 생성
    """
    template = MissionTemplate(
        player_id=data.player_id,
        text=data.text,
        point=data.point,
        day_of_week=data.day_of_week,
        group_id=getattr(data, 'group_id', None),
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)

    # ★ 롤링 윈도우: 즉시 미션 생성
    start, end = get_rolling_window()
    await generate_missions_for_range(db, start, end)

    return MissionTemplateResponse.model_validate(template)


async def _propagate_template_change(
    db: AsyncSession,
    template_id: int,
    new_text: str,
    new_point: int,
    old_point: int,
) -> None:
    """템플릿 수정 시 기존 배정 미션 전파 (상태별 정책 적용)

    -- [SQL] 1) 비완료 미션 일괄 UPDATE (active/pending_approval/failed/rejected)
    -- UPDATE missions SET text = :text, point = :new_point, updated_at = NOW()
    -- WHERE template_id = :tid
    --   AND status IN ('active', 'pending_approval', 'failed', 'rejected')
    --   AND deleted_at IS NULL;
    --
    -- [SQL] 2) 완료 미션: 건수·날짜 조회 → point UPDATE → daily_points 차액 보정
    -- SELECT player_id, date FROM missions
    -- WHERE template_id = :tid AND status = 'completed' AND deleted_at IS NULL;
    --
    -- UPDATE missions SET text = :text, point = :new_point, updated_at = NOW()
    -- WHERE template_id = :tid AND status = 'completed' AND deleted_at IS NULL;
    --
    -- FOR each (player_id, date):
    --   UPDATE daily_points
    --   SET earned = earned + :delta, balance = balance + :delta
    --   WHERE player_id = :pid AND date = :date;
    """
    from sqlalchemy import update as sql_update
    from app.domains.mission.models import Mission

    now_utc = datetime.now(timezone.utc)
    delta = new_point - old_point

    # 1) 비완료 미션: text + point 직접 갱신
    await db.execute(
        sql_update(Mission)
        .where(
            Mission.template_id == template_id,
            Mission.status.in_(["active", "pending_approval", "failed", "rejected"]),
            Mission.deleted_at.is_(None),
        )
        .values(text=new_text, point=new_point, updated_at=now_utc)
    )

    # 2) 완료 미션: 먼저 (player_id, date) 수집 → 이후 daily_points 차액 보정
    completed_result = await db.execute(
        select(Mission.player_id, Mission.date).where(
            Mission.template_id == template_id,
            Mission.status == "completed",
            Mission.deleted_at.is_(None),
        )
    )
    completed_rows = completed_result.all()

    # 완료 미션 text + point 갱신
    await db.execute(
        sql_update(Mission)
        .where(
            Mission.template_id == template_id,
            Mission.status == "completed",
            Mission.deleted_at.is_(None),
        )
        .values(text=new_text, point=new_point, updated_at=now_utc)
    )

    # daily_points 차액 보정 + total_earned 보정 (포인트가 변경된 경우에만)
    if delta != 0 and completed_rows:
        from app.domains.daily_point.service import adjust_daily_point
        from app.domains.daily_point.schema import DailyPointAdjust
        from app.domains.mission.service import _sync_total_earned
        from collections import defaultdict

        # daily_points: 날짜별 1건씩 보정
        for row in completed_rows:
            await adjust_daily_point(db, DailyPointAdjust(
                player_id=row.player_id,
                date=row.date,
                earned_delta=delta,
                spent_delta=0,
            ))

        # total_earned: 플레이어별 완료 미션 수 × delta → 1회 호출
        player_count: dict[int, int] = defaultdict(int)
        for row in completed_rows:
            player_count[row.player_id] += 1

        for pid, count in player_count.items():
            await _sync_total_earned(db, pid, delta * count)


async def update_template(db: AsyncSession, template_id: int, data: MissionTemplateUpdate) -> MissionTemplateResponse:
    """
    -- [SQL] 템플릿 수정 + 배정 미션 전파
    -- UPDATE mission_templates SET text=:text, point=:point, day_of_week=:dow, is_active=:active
    -- WHERE id = :id AND deleted_at IS NULL;
    --
    -- 전파 정책 (_propagate_template_change):
    --   active/pending_approval/failed/rejected → text + point 직접 UPDATE
    --   completed → text + point UPDATE + daily_points 차액 보정
    --
    -- day_of_week 변경 시: 미래 active 미션 Soft Delete → 롤링 윈도우 재생성
    """
    from datetime import timedelta
    from sqlalchemy import update as sql_update
    from app.domains.mission.models import Mission

    result = await db.execute(
        select(MissionTemplate).where(
            MissionTemplate.id == template_id, MissionTemplate.deleted_at.is_(None)
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    old_point = template.point
    old_day_of_week = template.day_of_week

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    await db.flush()

    new_text = template.text
    new_point = template.point
    day_changed = old_day_of_week != template.day_of_week

    # ★ 상태별 전파: 기존 배정 미션 text/point 갱신 + 완료 미션 daily_points 보정
    await _propagate_template_change(db, template_id, new_text, new_point, old_point)

    # ★ 요일 변경 시: 미래 active 미션 재생성
    #    _propagate_template_change에서 이미 갱신됐지만 요일이 맞지 않는 날짜는 삭제 후 재생성
    if day_changed:
        today = date.today()
        now_utc = datetime.now(timezone.utc)
        await db.execute(
            sql_update(Mission)
            .where(
                Mission.template_id == template_id,
                Mission.status == "active",
                Mission.date > today,
                Mission.deleted_at.is_(None),
            )
            .values(deleted_at=now_utc, msg="[시스템] 스케줄 수정으로 인한 재생성")
        )
        _, end_date = get_rolling_window()
        tomorrow = today + timedelta(days=1)
        await generate_missions_for_range(db, tomorrow, end_date)

    await db.refresh(template)
    return MissionTemplateResponse.model_validate(template)


async def delete_template(db: AsyncSession, template_id: int) -> None:
    """
    -- [SQL] 템플릿 삭제 및 관련 미션 일괄 정리 (Option B + 주간 범위 한정)
    --
    -- 1. 템플릿 Soft Delete
    -- UPDATE mission_templates SET deleted_at = NOW()
    -- WHERE id = :template_id AND deleted_at IS NULL;
    --
    -- 2. 해당 템플릿 기반 미완료 미션 Soft Delete (이번 주 범위 한정)
    -- UPDATE missions
    -- SET deleted_at = NOW(), msg = '[시스템] 스케줄 삭제로 인한 자동 취소'
    -- WHERE player_id = :pid AND text = :text AND point = :point
    --   AND proposed_by = 'template' AND status = 'active'
    --   AND date >= :week_start AND date <= :week_end
    --   AND deleted_at IS NULL;
    """
    from datetime import timedelta
    from sqlalchemy import update as sql_update
    from app.domains.mission.models import Mission

    # 1. 템플릿 조회
    result = await db.execute(
        select(MissionTemplate).where(
            MissionTemplate.id == template_id, MissionTemplate.deleted_at.is_(None)
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 2. 롤링 윈도우 범위 계산 (이번 주 월요일 ~ 다음 주 일요일)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())        # 이번 주 월요일
    _, rolling_end = get_rolling_window()                       # 다음 주 일요일까지
    week_end = rolling_end

    # 3. 관련 미션 연쇄 Soft Delete (이번 주, active만)
    now_utc = datetime.now(timezone.utc)
    cleanup_stmt = (
        sql_update(Mission)
        .where(
            Mission.player_id == template.player_id,
            Mission.text == template.text,
            Mission.point == template.point,
            Mission.proposed_by == "template",
            Mission.status == "active",
            Mission.date >= week_start,
            Mission.date <= week_end,
            Mission.deleted_at.is_(None),
        )
        .values(
            deleted_at=now_utc,
            msg="[시스템] 스케줄 삭제로 인한 자동 취소",
        )
    )
    await db.execute(cleanup_stmt)

    # 4. 템플릿 본체 Soft Delete
    template.deleted_at = now_utc
    await db.flush()


async def delete_templates_by_group(db: AsyncSession, group_id: str) -> None:
    """
    -- [SQL] group_id가 동일한 템플릿 전체 Soft Delete + 관련 미션 연쇄 정리
    -- SELECT * FROM mission_templates WHERE group_id = :group_id AND deleted_at IS NULL;
    -- for each: 개별 delete_template 호출 (cascade 미션 정리 포함)
    """
    result = await db.execute(
        select(MissionTemplate).where(
            MissionTemplate.group_id == group_id,
            MissionTemplate.deleted_at.is_(None),
        )
    )
    templates = result.scalars().all()
    for tmpl in templates:
        await delete_template(db, tmpl.id)


async def generate_missions_from_templates(db: AsyncSession, target_date: date) -> int:
    """
    Lazy Init: 오늘 요일에 해당하는 활성 템플릿을 missions에 자동 생성.
    중복 방지: last_generated_date가 target_date와 같으면 스킵.
    추가 방어: (player_id, date, text, point) 조합으로 이미 존재하면 스킵.

    -- [SQL] Lazy Init 조회
    -- SELECT * FROM mission_templates
    -- WHERE is_active = TRUE AND deleted_at IS NULL
    --   AND (last_generated_date IS NULL OR last_generated_date < :target_date);
    --
    -- [SQL] 중복 확인
    -- SELECT 1 FROM missions
    -- WHERE player_id = :pid AND date = :date AND text = :text AND point = :point
    --   AND deleted_at IS NULL LIMIT 1;
    --
    -- [SQL] 미션 생성
    -- INSERT INTO missions (player_id, date, text, point, status, sender, proposed_by, sort_order)
    -- VALUES (:pid, :date, :text, :point, 'active', '관리자', 'template', :order);
    """
    from app.domains.mission.models import Mission

    stmt = select(MissionTemplate).where(
        MissionTemplate.is_active.is_(True),
        MissionTemplate.deleted_at.is_(None),
        (MissionTemplate.last_generated_date.is_(None))
        | (MissionTemplate.last_generated_date < target_date),
    )
    result = await db.execute(stmt)
    templates = result.scalars().all()

    created_count = 0
    for tmpl in templates:
        if not matches_day(tmpl.day_of_week, target_date):
            continue

        # 중복 확인
        dup_check = await db.execute(
            select(Mission.id).where(
                Mission.player_id == tmpl.player_id,
                Mission.date == target_date,
                Mission.text == tmpl.text,
                Mission.point == tmpl.point,
                Mission.deleted_at.is_(None),
            ).limit(1)
        )
        if dup_check.scalar_one_or_none() is not None:
            # 이미 존재 → last_generated_date만 갱신
            tmpl.last_generated_date = target_date
            continue

        # 미션 생성
        mission = Mission(
            player_id=tmpl.player_id,
            date=target_date,
            text=tmpl.text,
            point=tmpl.point,
            status="active",
            sender="관리자",
            proposed_by="template",
            sort_order=0,
            template_id=tmpl.id,
        )
        db.add(mission)
        tmpl.last_generated_date = target_date
        created_count += 1

    await db.flush()
    return created_count


async def batch_delete_template_and_missions(
    db: AsyncSession,
    template_ids: list[int],
    delete_missions: bool = False,
    mission_date_start: date | None = None,
    mission_date_end: date | None = None,
) -> dict:
    """
    -- [SQL] 반복미션 일괄삭제
    --
    -- 1. 대상 템플릿 조회
    -- SELECT * FROM mission_templates WHERE id IN (:ids) AND deleted_at IS NULL;
    --
    -- 2. 템플릿 소프트 삭제
    -- UPDATE mission_templates SET deleted_at = NOW() WHERE id IN (:ids);
    --
    -- 3. (delete_missions=true) 생성된 미션 소프트 삭제
    --    completed 미션은 제외, pending_approval 포함
    -- UPDATE missions SET deleted_at = NOW()
    -- WHERE player_id = :pid AND text = :text
    --   AND date BETWEEN :start AND :end
    --   AND status != 'completed' AND deleted_at IS NULL;
    """
    from datetime import datetime, timezone
    from app.domains.mission.models import Mission

    now_utc = datetime.now(timezone.utc)

    # 1. 대상 템플릿 조회
    stmt = select(MissionTemplate).where(
        MissionTemplate.id.in_(template_ids),
        MissionTemplate.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    templates = result.scalars().all()

    if not templates:
        raise HTTPException(status_code=404, detail="삭제할 템플릿을 찾을 수 없습니다")

    # 2. 템플릿 소프트 삭제
    template_count = 0
    for tmpl in templates:
        tmpl.deleted_at = now_utc
        template_count += 1

    # 3. 생성된 미션 삭제 (옵션)
    mission_count = 0
    pending_count = 0
    if delete_missions and mission_date_start and mission_date_end:
        for tmpl in templates:
            # pending_approval 건수 조회 (경고용)
            pending_stmt = select(func.count()).where(
                Mission.player_id == tmpl.player_id,
                Mission.text == tmpl.text,
                Mission.date >= mission_date_start,
                Mission.date <= mission_date_end,
                Mission.status == "pending_approval",
                Mission.deleted_at.is_(None),
            )
            pending_result = await db.execute(pending_stmt)
            pending_count += pending_result.scalar() or 0

            # completed 제외, 나머지 삭제
            mission_stmt = (
                sql_update(Mission)
                .where(
                    Mission.player_id == tmpl.player_id,
                    Mission.text == tmpl.text,
                    Mission.date >= mission_date_start,
                    Mission.date <= mission_date_end,
                    Mission.status != "completed",
                    Mission.deleted_at.is_(None),
                )
                .values(deleted_at=now_utc)
            )
            result = await db.execute(mission_stmt)
            mission_count += result.rowcount

    await db.flush()

    return {
        "deleted_templates": template_count,
        "deleted_missions": mission_count,
        "preserved_completed": "completed 미션은 보존됨",
        "pending_deleted": pending_count,
    }


async def batch_delete_preview(
    db: AsyncSession,
    template_ids: list[int],
    delete_missions: bool = False,
    mission_date_start: date | None = None,
    mission_date_end: date | None = None,
) -> dict:
    """
    -- [SQL] 반복미션 일괄삭제 미리보기 (실제 삭제 없이 영향 범위 반환)
    -- SELECT COUNT(*) FROM mission_templates WHERE id IN (:ids) AND deleted_at IS NULL;
    -- SELECT COUNT(*) FROM missions WHERE ... (조건별 건수)
    """
    from app.domains.mission.models import Mission

    # 템플릿 건수
    tmpl_stmt = select(func.count()).where(
        MissionTemplate.id.in_(template_ids),
        MissionTemplate.deleted_at.is_(None),
    )
    tmpl_result = await db.execute(tmpl_stmt)
    template_count = tmpl_result.scalar() or 0

    mission_count = 0
    completed_count = 0
    pending_count = 0

    if delete_missions and mission_date_start and mission_date_end:
        templates = (await db.execute(
            select(MissionTemplate).where(
                MissionTemplate.id.in_(template_ids),
                MissionTemplate.deleted_at.is_(None),
            )
        )).scalars().all()

        for tmpl in templates:
            base_where = [
                Mission.player_id == tmpl.player_id,
                Mission.text == tmpl.text,
                Mission.date >= mission_date_start,
                Mission.date <= mission_date_end,
                Mission.deleted_at.is_(None),
            ]

            # 삭제 대상 (completed 제외)
            active_stmt = select(func.count()).where(*base_where, Mission.status != "completed")
            mission_count += (await db.execute(active_stmt)).scalar() or 0

            # 보존 대상 (completed)
            comp_stmt = select(func.count()).where(*base_where, Mission.status == "completed")
            completed_count += (await db.execute(comp_stmt)).scalar() or 0

            # 경고 대상 (pending_approval)
            pend_stmt = select(func.count()).where(*base_where, Mission.status == "pending_approval")
            pending_count += (await db.execute(pend_stmt)).scalar() or 0

    return {
        "template_count": template_count,
        "mission_count": mission_count,
        "completed_count": completed_count,
        "pending_count": pending_count,
    }


async def get_week_remaining_missions(
    db: AsyncSession, player_id: int, start_date: date, end_date: date
) -> list[dict]:
    """
    주간 남은 미션 조회: start_date~end_date 범위에서 status='active'인 미션 목록 반환.

    -- [SQL] 주간 남은 미션
    -- SELECT id, date, text, point, status FROM missions
    -- WHERE player_id = :pid AND date BETWEEN :start AND :end
    --   AND status = 'active' AND deleted_at IS NULL
    -- ORDER BY date ASC, sort_order ASC;
    """
    stmt = (
        select(Mission)
        .where(
            Mission.player_id == player_id,
            Mission.date >= start_date,
            Mission.date <= end_date,
            Mission.status == "active",
            Mission.deleted_at.is_(None),
        )
        .order_by(Mission.date.asc(), Mission.sort_order.asc())
    )
    result = await db.execute(stmt)
    missions = result.scalars().all()
    return [
        {
            "id": m.id,
            "date": str(m.date),
            "text": m.text,
            "point": m.point,
            "status": m.status,
        }
        for m in missions
    ]
