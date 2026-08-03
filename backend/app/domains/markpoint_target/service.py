"""Target Markpoint application service.  All write paths commit once."""
from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family import service as family_service
from app.domains.family.models import FamilyMembership
from app.domains.level_tier.service import calculate_level, get_tiers_by_job
from app.domains.markpoint_access import service as access_service
from app.domains.service_outbox import service as outbox_service
from .models import MarkpointAuditEvent, MarkpointBalanceProjection, MarkpointLedgerEntry, MarkpointMission, MarkpointMissionTemplate

SERVICE_CODE = "markpoint"
MISSION_MANAGE = "markpoint.missions.manage"
POINTS_ADJUST = "markpoint.points.adjust"
OWN_READ = "markpoint.own.read"

# Same convention as app/domains/daily_point/service.py's own `KST` --
# "today" is a Family-facing business calendar date, not whatever timezone
# the server process's OS happens to be set to. `date.today()` reads that
# OS-local clock, which drifts a full calendar day away from the Ledger's
# UTC-stored `occurred_at` for roughly nine hours out of every KST day
# (RE-QA-F-003: `today_earned`/`today_deducted` measured 0 instead of their
# real value whenever the two didn't agree, reproduced deterministically
# via a live UTC/KST offset, not tied to any DB run count or fixture order).
KST = ZoneInfo("Asia/Seoul")


def _today_kst() -> date:
    return datetime.now(KST).date()


def _now(): return datetime.now(timezone.utc)

async def require_access(db: AsyncSession, membership: FamilyMembership) -> None:
    state = await access_service.get_access_status(db, membership)
    if not state["has_default_access"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Markpoint 접근 권한이 없습니다")

async def require_permission(db: AsyncSession, membership: FamilyMembership, permission: str) -> None:
    await require_access(db, membership)
    if permission not in await family_service.effective_permissions(db, membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다")

async def reviewer_display_name(db: AsyncSession, membership_id: int) -> str:
    """Resolve a reviewer Membership's human-readable name, same cross-domain
    shape as wagle's `participant_display_name` -- through the family
    domain's own public service function, not a raw cross-domain query."""
    membership = await db.get(FamilyMembership, membership_id)
    if membership is None:
        return ""
    account = await family_service.get_account(db, membership.account_id)
    return account.display_name if account else ""

async def mission_out(db: AsyncSession, mission: MarkpointMission) -> "MissionOut":
    from .schemas import MissionOut, ChecklistItem
    reviewer_name = await reviewer_display_name(db, mission.approved_by_membership_id) if mission.approved_by_membership_id else None
    return MissionOut(
        id=mission.id, family_group_id=mission.family_group_id, assignee_membership_id=mission.assignee_membership_id,
        title=mission.title, description=mission.description, scheduled_for=mission.scheduled_for,
        reward_amount=mission.reward_amount, status=mission.status,
        checklist=[ChecklistItem(**item) for item in mission.checklist] if mission.checklist else None,
        rejection_reason=mission.rejection_reason, reviewer_display_name=reviewer_name or None,
    )

async def _member(db, family_id: int, membership_id: int) -> FamilyMembership:
    row = await db.get(FamilyMembership, membership_id)
    if row is None or row.family_group_id != family_id or row.status != "active" or row.deleted_at is not None:
        raise HTTPException(status_code=404, detail="활성 가족 구성원을 찾을 수 없습니다")
    await require_access(db, row)
    return row

def _audit(db, family_id, actor_id, action, aggregate_type, aggregate_id, payload=None):
    db.add(MarkpointAuditEvent(family_group_id=family_id, actor_membership_id=actor_id, action=action, aggregate_type=aggregate_type, aggregate_id=str(aggregate_id), payload=payload or {}))

async def create_mission(db: AsyncSession, family_id: int, actor: FamilyMembership, *, assignee_id: int, title: str, scheduled_for: date, reward_amount: int, description: str | None = None, checklist: list[str] | None = None) -> MarkpointMission:
    await require_permission(db, actor, MISSION_MANAGE)
    await _member(db, family_id, assignee_id)
    initial_checklist = [{"label": label, "done": False} for label in checklist] if checklist else None
    mission = MarkpointMission(family_group_id=family_id, assignee_membership_id=assignee_id, created_by_membership_id=actor.id, title=title, description=description, scheduled_for=scheduled_for, reward_amount=reward_amount, checklist=initial_checklist, status="active")
    db.add(mission); await db.flush(); _audit(db, family_id, actor.id, "mission.created", "mission", mission.id, {"assignee_membership_id": assignee_id}); await db.commit(); await db.refresh(mission); return mission

async def update_mission_checklist(db: AsyncSession, family_id: int, actor: FamilyMembership, mission_id: int, items: list[dict]) -> MarkpointMission:
    """Assignee toggles their own checklist before submitting. Not a MISSION_MANAGE action --
    this is the assignee marking their own progress, the same ownership shape as `submit_mission`."""
    await require_access(db, actor)
    mission = await db.get(MarkpointMission, mission_id)
    if mission is None or mission.family_group_id != family_id or mission.assignee_membership_id != actor.id:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    if mission.status not in ("active",):
        raise HTTPException(status_code=409, detail="체크리스트를 수정할 수 없는 미션 상태입니다")
    if not mission.checklist or len(items) != len(mission.checklist):
        raise HTTPException(status_code=422, detail="체크리스트 항목 수가 일치하지 않습니다")
    mission.checklist = [{"label": mission.checklist[i]["label"], "done": bool(item["done"])} for i, item in enumerate(items)]
    await db.commit(); await db.refresh(mission); return mission

async def create_template(db, family_id, actor, *, assignee_id, title, reward_amount, cycle_type, start_date, end_date, day_of_week):
    await require_permission(db, actor, MISSION_MANAGE); await _member(db, family_id, assignee_id)
    template=MarkpointMissionTemplate(family_group_id=family_id, assignee_membership_id=assignee_id, created_by_membership_id=actor.id, title=title, reward_amount=reward_amount, cycle_type=cycle_type, start_date=start_date, end_date=end_date, day_of_week=day_of_week)
    db.add(template); await db.flush(); _audit(db,family_id,actor.id,"template.created","template",template.id); await db.commit(); await db.refresh(template); return template

async def list_templates(db, family_id, actor):
    await require_permission(db, actor, MISSION_MANAGE)
    return list((await db.execute(select(MarkpointMissionTemplate).where(MarkpointMissionTemplate.family_group_id==family_id).order_by(MarkpointMissionTemplate.id))).scalars())

async def update_template(db,family_id,actor,template_id,values):
    await require_permission(db,actor,MISSION_MANAGE); template=await db.get(MarkpointMissionTemplate,template_id)
    if template is None or template.family_group_id!=family_id: raise HTTPException(status_code=404,detail="미션 템플릿을 찾을 수 없습니다")
    for key,value in values.items():
        if value is not None: setattr(template,key,value)
    _audit(db,family_id,actor.id,"template.updated","template",template.id); await db.commit(); await db.refresh(template); return template

async def deactivate_template(db,family_id,actor,template_id):
    await require_permission(db,actor,MISSION_MANAGE); template=await db.get(MarkpointMissionTemplate,template_id)
    if template is None or template.family_group_id!=family_id: raise HTTPException(status_code=404,detail="미션 템플릿을 찾을 수 없습니다")
    template.status="cancelled"; _audit(db,family_id,actor.id,"template.deactivated","template",template.id); await db.commit(); return template

async def materialize_template(db: AsyncSession, family_id: int, actor: FamilyMembership, template_id: int, scheduled_for: date) -> MarkpointMission:
    await require_permission(db, actor, MISSION_MANAGE)
    template = await db.get(MarkpointMissionTemplate, template_id)
    if template is None or template.family_group_id != family_id or template.status != "active": raise HTTPException(status_code=404, detail="미션 템플릿을 찾을 수 없습니다")
    mission = MarkpointMission(family_group_id=family_id, assignee_membership_id=template.assignee_membership_id, created_by_membership_id=actor.id, template_id=template.id, title=template.title, scheduled_for=scheduled_for, reward_amount=template.reward_amount, status="active")
    try:
        db.add(mission); await db.flush()
    except IntegrityError:
        await db.rollback()
        existing=(await db.execute(select(MarkpointMission).where(MarkpointMission.template_id==template.id, MarkpointMission.scheduled_for==scheduled_for))).scalars().one()
        return existing
    _audit(db, family_id, actor.id, "mission.materialized", "mission", mission.id, {"template_id": template.id})
    await db.commit(); await db.refresh(mission); return mission

async def submit_mission(db: AsyncSession, family_id: int, actor: FamilyMembership, mission_id: int) -> MarkpointMission:
    await require_access(db, actor)
    mission = await db.get(MarkpointMission, mission_id)
    if mission is None or mission.family_group_id != family_id or mission.assignee_membership_id != actor.id: raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    if mission.status != "active": raise HTTPException(status_code=409, detail="제출할 수 없는 미션 상태입니다")
    mission.status="pending_approval"; mission.submitted_at=_now(); _audit(db, family_id, actor.id, "mission.submitted", "mission", mission.id); await db.commit(); await db.refresh(mission); return mission

async def _projection(db, family_id, member_id):
    row=(await db.execute(select(MarkpointBalanceProjection).where(MarkpointBalanceProjection.family_group_id==family_id, MarkpointBalanceProjection.family_membership_id==member_id).with_for_update())).scalars().first()
    if row is None:
        row=MarkpointBalanceProjection(family_group_id=family_id, family_membership_id=member_id); db.add(row); await db.flush()
    return row

async def _entry(db, *, family_id, member_id, amount, entry_type, source_type, source_identifier, idempotency_key, actor_id, reason=None, reversal_of=None):
    existing=(await db.execute(select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.family_group_id==family_id, MarkpointLedgerEntry.idempotency_key==idempotency_key))).scalars().first()
    if existing: return existing, False
    entry=MarkpointLedgerEntry(family_group_id=family_id, family_membership_id=member_id, amount=amount, entry_type=entry_type, source_type=source_type, source_identifier=source_identifier, idempotency_key=idempotency_key, created_by_membership_id=actor_id, reason=reason, reversal_of_entry_id=reversal_of)
    try:
        async with db.begin_nested(): db.add(entry); await db.flush()
    except IntegrityError:
        entry=(await db.execute(select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.family_group_id==family_id, MarkpointLedgerEntry.idempotency_key==idempotency_key))).scalars().one(); return entry, False
    projection=await _projection(db, family_id, member_id); projection.current_balance += amount
    if entry_type in ("MISSION_REWARD", "MANUAL_CREDIT", "CORRECTION") and amount > 0: projection.lifetime_earned += amount
    elif entry_type == "REVERSAL" and amount < 0: projection.lifetime_earned = max(0, projection.lifetime_earned + amount)
    elif amount < 0: projection.lifetime_spent += -amount
    projection.version += 1
    return entry, True

async def approve_mission(db: AsyncSession, family_id: int, actor: FamilyMembership, mission_id: int) -> MarkpointMission:
    await require_permission(db, actor, MISSION_MANAGE)
    mission=(await db.execute(select(MarkpointMission).where(MarkpointMission.id==mission_id, MarkpointMission.family_group_id==family_id).with_for_update())).scalars().first()
    if mission is None: raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다")
    if mission.status == "completed": return mission
    if mission.status != "pending_approval": raise HTTPException(status_code=409, detail="승인할 수 없는 미션 상태입니다")
    await _member(db, family_id, mission.assignee_membership_id)
    entry, inserted=await _entry(db, family_id=family_id, member_id=mission.assignee_membership_id, amount=mission.reward_amount, entry_type="MISSION_REWARD", source_type="mission_approval", source_identifier=str(mission.id), idempotency_key=f"mission-approved:{mission.id}", actor_id=actor.id)
    mission.status="completed"; mission.approved_by_membership_id=actor.id; mission.completed_at=_now()
    if inserted:
        await outbox_service.enqueue_event(db, owner_service=SERVICE_CODE, event_type="mission.approved", event_version=1, aggregate_type="mission", aggregate_id=str(mission.id), source_event_id=f"mission-approved:{mission.id}", family_id=family_id, payload={"family_group_id": family_id, "mission_id": mission.id, "assignee_membership_id": mission.assignee_membership_id, "reward_amount": mission.reward_amount})
    _audit(db, family_id, actor.id, "mission.approved", "mission", mission.id, {"ledger_entry_id": entry.id}); await db.commit(); await db.refresh(mission); return mission

async def reverse_mission_reward(db: AsyncSession, family_id: int, actor: FamilyMembership, mission_id: int, reason: str) -> MarkpointMission:
    await require_permission(db, actor, MISSION_MANAGE)
    mission=(await db.execute(select(MarkpointMission).where(MarkpointMission.id==mission_id, MarkpointMission.family_group_id==family_id).with_for_update())).scalars().first()
    if mission is None or mission.status != "completed": raise HTTPException(status_code=409, detail="되돌릴 승인 보상이 없습니다")
    original=(await db.execute(select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.family_group_id==family_id, MarkpointLedgerEntry.source_type=="mission_approval", MarkpointLedgerEntry.source_identifier==str(mission.id)))).scalars().one()
    await _entry(db, family_id=family_id, member_id=mission.assignee_membership_id, amount=-original.amount, entry_type="REVERSAL", source_type="mission_reversal", source_identifier=str(mission.id), idempotency_key=f"mission-reversal:{mission.id}", actor_id=actor.id, reason=reason, reversal_of=original.id)
    mission.status="rejected"; mission.rejection_reason=reason; _audit(db, family_id, actor.id, "mission.reversed", "mission", mission.id); await db.commit(); await db.refresh(mission); return mission

async def reject_mission(db,family_id,actor,mission_id,reason):
    await require_permission(db,actor,MISSION_MANAGE)
    mission=await db.get(MarkpointMission,mission_id)
    if mission is None or mission.family_group_id!=family_id: raise HTTPException(status_code=404,detail="미션을 찾을 수 없습니다")
    if mission.status=="rejected": return mission
    if mission.status!="pending_approval": raise HTTPException(status_code=409,detail="반려할 수 없는 미션 상태입니다")
    if not reason: raise HTTPException(status_code=422,detail="반려 사유가 필요합니다")
    mission.status="rejected"; mission.rejection_reason=reason; mission.approved_by_membership_id=actor.id; _audit(db,family_id,actor.id,"mission.rejected","mission",mission.id,{"reason":reason}); await db.commit(); await db.refresh(mission); return mission

async def cancel_mission(db,family_id,actor,mission_id,reason):
    await require_permission(db,actor,MISSION_MANAGE)
    mission=await db.get(MarkpointMission,mission_id)
    if mission is None or mission.family_group_id!=family_id: raise HTTPException(status_code=404,detail="미션을 찾을 수 없습니다")
    if mission.status=="cancelled": return mission
    if mission.status=="completed":
        await reverse_mission_reward(db,family_id,actor,mission.id,reason or "cancelled")
        mission=await db.get(MarkpointMission,mission_id)
    elif mission.status not in ("active","pending_approval","rejected"): raise HTTPException(status_code=409,detail="취소할 수 없는 미션 상태입니다")
    mission.status="cancelled"; mission.cancelled_at=_now(); mission.rejection_reason=reason; _audit(db,family_id,actor.id,"mission.cancelled","mission",mission.id); await db.commit(); await db.refresh(mission); return mission

async def expire_stale_missions(db,family_id,actor,today=None):
    await require_permission(db,actor,MISSION_MANAGE); today=today or _today_kst()
    rows=list((await db.execute(select(MarkpointMission).where(MarkpointMission.family_group_id==family_id,MarkpointMission.status=="active",MarkpointMission.scheduled_for<today).with_for_update())).scalars())
    for mission in rows: mission.status="expired"; _audit(db,family_id,actor.id,"mission.expired","mission",mission.id)
    await db.commit(); return len(rows)

async def adjust_points(db: AsyncSession, family_id: int, actor: FamilyMembership, beneficiary_id: int, amount: int, reason: str, idempotency_key: str):
    await require_permission(db, actor, POINTS_ADJUST)
    await _member(db, family_id, beneficiary_id)
    if amount == 0: raise HTTPException(status_code=422, detail="조정 포인트는 0일 수 없습니다")
    entry, inserted=await _entry(db, family_id=family_id, member_id=beneficiary_id, amount=amount, entry_type="MANUAL_CREDIT" if amount>0 else "MANUAL_DEBIT", source_type="manual_adjustment", source_identifier=idempotency_key, idempotency_key=f"manual:{idempotency_key}", actor_id=actor.id, reason=reason)
    if inserted:
        await outbox_service.enqueue_event(db, owner_service=SERVICE_CODE, event_type="points.adjusted", event_version=1, aggregate_type="ledger_entry", aggregate_id=str(entry.id), source_event_id=f"manual:{idempotency_key}", family_id=family_id, payload={"family_group_id":family_id,"ledger_entry_id":entry.id,"amount":amount})
    _audit(db, family_id, actor.id, "points.adjusted", "ledger_entry", entry.id, {"amount": amount}); await db.commit(); await db.refresh(entry); return entry

async def self_spend(db: AsyncSession, family_id: int, membership: FamilyMembership, amount: int, reason: str, source_type: str, source_identifier: str, idempotency_key: str):
    """A member spending their own points (e.g. Reward redemption, W7.5
    SLICE-REWARD-CATALOG). Deliberately **not** `adjust_points`: that
    requires `POINTS_ADJUST`, an admin-only permission code no ordinary
    member (especially a child) holds -- this only ever debits the
    caller's own balance, gated by `require_access` alone, the same
    boundary every other `own_*` read already uses. `amount` must be
    negative; a positive self-credit is not this function's job."""
    await require_access(db, membership)
    if amount >= 0:
        raise HTTPException(status_code=422, detail="차감 금액은 음수여야 합니다")
    balance = await _projection(db, family_id, membership.id)
    if balance.current_balance + amount < 0:
        raise HTTPException(status_code=409, detail="포인트가 부족합니다")
    entry, inserted = await _entry(
        db, family_id=family_id, member_id=membership.id, amount=amount, entry_type="MANUAL_DEBIT",
        source_type=source_type, source_identifier=source_identifier, idempotency_key=idempotency_key,
        actor_id=membership.id, reason=reason,
    )
    _audit(db, family_id, membership.id, "points.self_spent", "ledger_entry", entry.id, {"amount": amount, "source_type": source_type})
    await db.commit()
    await db.refresh(entry)
    return entry

async def own_balance(db, family_id, membership):
    await require_access(db, membership); return await _projection(db, family_id, membership.id)
async def own_missions(db, family_id, membership):
    await require_access(db, membership); return list((await db.execute(select(MarkpointMission).where(MarkpointMission.family_group_id==family_id, MarkpointMission.assignee_membership_id==membership.id).order_by(MarkpointMission.scheduled_for.desc()))).scalars())
async def own_ledger(db, family_id, membership):
    await require_access(db, membership); return list((await db.execute(select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.family_group_id==family_id, MarkpointLedgerEntry.family_membership_id==membership.id).order_by(MarkpointLedgerEntry.id.desc()))).scalars())
async def own_level(db, family_id, membership):
    balance=await own_balance(db, family_id, membership); info=calculate_level(balance.lifetime_earned, await get_tiers_by_job(db)); return balance, info

async def own_summary(db,family_id,membership,anchor=None):
    await require_access(db,membership); anchor=anchor or _today_kst(); week_start=anchor-timedelta(days=anchor.weekday()); week_end=week_start+timedelta(days=6)
    ledger_today=(await db.execute(select(func.coalesce(func.sum(MarkpointLedgerEntry.amount),0)).where(MarkpointLedgerEntry.family_group_id==family_id,MarkpointLedgerEntry.family_membership_id==membership.id,MarkpointLedgerEntry.amount>0,func.date(func.timezone("Asia/Seoul",MarkpointLedgerEntry.occurred_at))==anchor))).scalar_one()
    remaining=(await db.execute(select(func.count()).select_from(MarkpointMission).where(MarkpointMission.family_group_id==family_id,MarkpointMission.assignee_membership_id==membership.id,MarkpointMission.scheduled_for.between(week_start,week_end),MarkpointMission.status.in_(("active","pending_approval"))))).scalar_one()
    balance=await _projection(db,family_id,membership.id)
    return {"family_group_id":family_id,"family_membership_id":membership.id,"today_earned":ledger_today,"remaining_missions":remaining,"current_balance":balance.current_balance,"week_start":week_start,"week_end":week_end}


# ===========================================================================
# MP-S04 — per-Family cycle configuration and its two guards
# ===========================================================================

# Reused from the legacy mission service rather than re-derived. The period
# arithmetic for all six cycles is the behaviour being preserved; a second
# implementation here could drift from the one the rest of the product uses.
from app.domains.mission.service import get_cycle_range  # noqa: E402
from app.domains.markpoint_target.models import MarkpointFamilyConfig  # noqa: E402

SUPPORTED_CYCLES = ("daily", "weekly", "biweekly", "monthly", "quarterly", "yearly")
DEFAULT_CYCLE = "weekly"
# Fields that Guard A does *not* protect. A cycle guard exists to stop the
# period boundaries moving under scheduled missions; a label has no such
# effect, and blocking it would make the guard feel arbitrary without making
# anything safer.
NON_CYCLE_FIELDS = ("display_name",)


async def get_family_config(db: AsyncSession, family_id: int) -> MarkpointFamilyConfig | None:
    return (
        await db.execute(
            select(MarkpointFamilyConfig).where(MarkpointFamilyConfig.family_group_id == family_id)
        )
    ).scalars().first()


async def read_family_config(db: AsyncSession, family_id: int, actor: FamilyMembership) -> dict:
    """Current configuration, or the documented default when none is set.

    Reading needs Markpoint access but not admin authority — a member has to be
    able to see which cycle their own missions are scored against.
    """
    await require_access(db, actor)
    row = await get_family_config(db, family_id)
    today = _today_kst()
    if row is None:
        start, end = get_cycle_range(DEFAULT_CYCLE, today)
        return {
            "family_group_id": family_id,
            "cycle_type": DEFAULT_CYCLE,
            "effective_from": start,
            "effective_to": end,
            "display_name": None,
            "configured": False,
        }
    return {
        "family_group_id": family_id,
        "cycle_type": row.cycle_type,
        "effective_from": row.effective_from,
        "effective_to": row.effective_to,
        "display_name": row.display_name,
        "configured": True,
    }


async def _assert_no_active_recurring_templates(db: AsyncSession, family_id: int) -> None:
    """Guard B — an ACTIVE recurring Template blocks a cycle change.

    Scoped to **this** Family's templates. A Family whose own templates are all
    inactive must stay changeable no matter how many templates other Families
    hold; the `family_group_id` predicate is what makes that true, and the test
    matrix asserts it from the other Family's side as well.
    """
    active = (
        await db.execute(
            select(func.count())
            .select_from(MarkpointMissionTemplate)
            .where(
                MarkpointMissionTemplate.family_group_id == family_id,
                MarkpointMissionTemplate.status == "active",
            )
        )
    ).scalar_one()
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"활성 반복 미션 템플릿이 {active}건 있어 주기를 변경할 수 없습니다. "
            "템플릿을 비활성화한 뒤 다시 시도해주세요.",
        )


def _assert_current_cycle_finished(row: MarkpointFamilyConfig, today: date) -> None:
    """Guard A — the running period cannot be changed while it is running.

    This is the legacy `validate_cycle_change` rule (`today <= cycle_end` →
    refuse), re-expressed against the Family's own stored period instead of a
    global one. The message keeps the remaining-days detail because that is the
    one piece of information that makes the refusal actionable.
    """
    if today <= row.effective_to:
        remaining = (row.effective_to - today).days
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"현재 주기({row.cycle_type}) 종료까지 {remaining}일 남았습니다. "
            f"{row.effective_to.isoformat()} 이후 변경 가능합니다.",
        )


async def update_family_config(
    db: AsyncSession,
    family_id: int,
    actor: FamilyMembership,
    *,
    cycle_type: str | None = None,
    display_name: str | None = None,
    today: date | None = None,
) -> dict:
    """Set this Family's Markpoint cycle.

    Authority is ServiceAdmin-level (`markpoint.missions.manage`), not
    FamilyAdmin. D4 is explicit that holding the family does not confer service
    administration, and migration `0006` removed the permission from every
    FAMILY-scope role precisely so this call cannot be reached by being an
    owner.

    There is **no force override**. No approved contract defines one, so none
    is offered — not to FamilyAdmin, not to ServiceAdmin. An override would be
    the natural place for a guard to quietly stop meaning anything.
    """
    await require_permission(db, actor, MISSION_MANAGE)
    today = today or _today_kst()
    row = await get_family_config(db, family_id)

    changing_cycle = cycle_type is not None and (row is None or cycle_type != row.cycle_type)

    if cycle_type is not None and cycle_type not in SUPPORTED_CYCLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"유효하지 않은 주기 값: '{cycle_type}'. 허용값: {', '.join(SUPPORTED_CYCLES)}",
        )

    if changing_cycle:
        # Order matters only for the error the caller sees first; both guards
        # are independent and either alone is sufficient to refuse.
        if row is not None:
            _assert_current_cycle_finished(row, today)
        await _assert_no_active_recurring_templates(db, family_id)

    if row is None:
        start, end = get_cycle_range(cycle_type or DEFAULT_CYCLE, today)
        row = MarkpointFamilyConfig(
            family_group_id=family_id,
            cycle_type=cycle_type or DEFAULT_CYCLE,
            effective_from=start,
            effective_to=end,
            display_name=display_name,
            updated_by_membership_id=actor.id,
        )
        db.add(row)
    else:
        if changing_cycle:
            start, end = get_cycle_range(cycle_type, today)
            row.cycle_type = cycle_type
            row.effective_from = start
            row.effective_to = end
        if display_name is not None:
            # Deliberately outside the guard: see NON_CYCLE_FIELDS.
            row.display_name = display_name
        row.updated_by_membership_id = actor.id

    _audit(
        db,
        family_id,
        actor.id,
        "markpoint.cycle_config.updated",
        "family_config",
        str(family_id),
        {"cycle_type": row.cycle_type, "cycle_changed": changing_cycle},
    )
    await db.commit()
    await db.refresh(row)
    return await read_family_config(db, family_id, actor)


# ===========================================================================
# MP-M03 — rolling materialization
# ===========================================================================


def rolling_window(today: date | None = None) -> tuple[date, date]:
    """The inclusive materialization window: today through next week's Sunday.

    Canonical contract, PM-approved 2026-08-01:
    ``TODAY_THROUGH_NEXT_WEEK_SUNDAY_INCLUSIVE``.

    The end is the Sunday *following* the current week's Sunday, so the window
    always spans the remainder of this week plus all of the next. Both
    endpoints are included, which is why the counts below are not multiples of
    seven:

        Monday   2026-03-30 -> 2026-04-12   14 inclusive dates
        Saturday 2026-04-04 -> 2026-04-12    9 inclusive dates
        Sunday   2026-04-05 -> 2026-04-12    8 inclusive dates

    A Monday therefore yields a fortnight, not a single week. Narrowing this to
    "this week's Sunday" would halve how many missions every Monday generates,
    so it is a product decision rather than a tidy-up.

    `mission_template.service.get_rolling_window` computes the same window; the
    two were verified to agree across 400 consecutive start dates.
    """
    today = today or _today_kst()
    this_sunday = today + timedelta(days=6 - today.weekday())
    return today, this_sunday + timedelta(days=7)


def _template_occurrence_dates(
    template: MarkpointMissionTemplate, window_start: date, window_end: date
) -> list[date]:
    """Dates inside the window on which this Template should have a Mission.

    Bounded by the Template's own `start_date`/`end_date` first: a rolling
    window may legitimately reach past the end of a Template's life, and
    materializing beyond it would resurrect a finished obligation.
    """
    start = max(window_start, template.start_date)
    end = window_end if template.end_date is None else min(window_end, template.end_date)
    if start > end:
        return []

    dates: list[date] = []
    cursor = start
    while cursor <= end:
        if template.cycle_type == "daily":
            dates.append(cursor)
        elif template.day_of_week is None:
            # No weekday pinned: one occurrence per cycle period, on the first
            # in-window day of that period. Anchoring on the period rather than
            # on the window keeps two overlapping windows agreeing on the date.
            period_start, _ = get_cycle_range(template.cycle_type, cursor)
            candidate = max(period_start, template.start_date)
            if window_start <= candidate <= end and candidate not in dates:
                dates.append(candidate)
        elif cursor.weekday() == template.day_of_week:
            dates.append(cursor)
        cursor += timedelta(days=1)
    return dates


async def materialize_rolling_window(
    db: AsyncSession,
    family_id: int,
    actor: FamilyMembership,
    *,
    template_id: int | None = None,
    today: date | None = None,
) -> dict:
    """Generate the window's missions for one Template, or for all active ones.

    Three properties this must hold, each of which has its own test:

    - **Only the Template's named assignee.** Never every ACTIVE membership,
      never everyone with Markpoint access, never the FamilyAdmin by default.
      A Template carries exactly one `assignee_membership_id` and that is the
      only person who gets a Mission.
    - **Exactly once per (template, date).** Enforced by the
      `uq_markpoint_mission_template_date` unique constraint and an
      `IntegrityError` catch inside a SAVEPOINT — not by a check-then-insert,
      which two concurrent callers both pass.
    - **This Family only.** Every query is `family_group_id`-scoped, so a
      second Family's templates are neither read nor written.
    """
    await require_permission(db, actor, MISSION_MANAGE)
    window_start, window_end = rolling_window(today)

    stmt = select(MarkpointMissionTemplate).where(
        MarkpointMissionTemplate.family_group_id == family_id,
        MarkpointMissionTemplate.status == "active",
    )
    if template_id is not None:
        stmt = stmt.where(MarkpointMissionTemplate.id == template_id)
    templates = list((await db.execute(stmt)).scalars())

    if template_id is not None and not templates:
        raise HTTPException(status_code=404, detail="활성 미션 템플릿을 찾을 수 없습니다")

    created, skipped = 0, 0
    for template in templates:
        for scheduled_for in _template_occurrence_dates(template, window_start, window_end):
            mission = MarkpointMission(
                family_group_id=family_id,
                assignee_membership_id=template.assignee_membership_id,
                created_by_membership_id=actor.id,
                template_id=template.id,
                title=template.title,
                scheduled_for=scheduled_for,
                reward_amount=template.reward_amount,
                status="active",
            )
            try:
                # SAVEPOINT so a duplicate loses only its own insert; the rest
                # of the batch stays in the same transaction.
                async with db.begin_nested():
                    db.add(mission)
                    await db.flush()
                created += 1
            except IntegrityError:
                skipped += 1

    _audit(
        db,
        family_id,
        actor.id,
        "mission.rolling_materialized",
        "template",
        str(template_id or "all"),
        {"created": created, "skipped": skipped, "window": [window_start.isoformat(), window_end.isoformat()]},
    )
    await db.commit()
    return {
        "window_start": window_start,
        "window_end": window_end,
        "templates_processed": len(templates),
        "missions_created": created,
        "missions_skipped_existing": skipped,
    }


# ===========================================================================
# MP-M04 / MP-P02 — weekly detail and daily/weekly projection
# ===========================================================================


def _period_for(config_cycle: str, anchor: date) -> tuple[date, date]:
    return get_cycle_range(config_cycle, anchor)


async def _sum_ledger(
    db: AsyncSession, family_id: int, member_id: int, *, positive: bool, start: date, end: date
) -> int:
    """Sum signed Ledger amounts in a date range.

    The Ledger is the source of truth for every figure below — there is no
    separate mutable daily total. Legacy kept a `daily_points` row that could
    disagree with its own history; deriving from the Ledger makes that class of
    divergence impossible rather than merely unlikely.

    `start`/`end` are KST calendar dates (see `_today_kst`), so `occurred_at`
    (an absolute UTC instant) must be converted to KST wall-clock time before
    its date is extracted — comparing under the session's plain UTC date
    (`func.date(occurred_at)` alone) silently disagreed with the KST anchor
    for roughly nine hours out of every day (RE-QA-F-003).
    """
    condition = MarkpointLedgerEntry.amount > 0 if positive else MarkpointLedgerEntry.amount < 0
    occurred_date_kst = func.date(func.timezone("Asia/Seoul", MarkpointLedgerEntry.occurred_at))
    total = (
        await db.execute(
            select(func.coalesce(func.sum(MarkpointLedgerEntry.amount), 0)).where(
                MarkpointLedgerEntry.family_group_id == family_id,
                MarkpointLedgerEntry.family_membership_id == member_id,
                condition,
                occurred_date_kst >= start,
                occurred_date_kst <= end,
            )
        )
    ).scalar_one()
    # Debits are stored negative; report them as a positive magnitude so a
    # caller never has to remember the sign convention to render "spent".
    return int(total) if positive else -int(total)


async def own_projection(db: AsyncSession, family_id: int, membership: FamilyMembership, anchor: date | None = None) -> dict:
    """Daily and weekly aggregates, all derived from the Ledger.

    `weekly_*` follows the **Family's configured cycle**, not a hardcoded week:
    a Family on `monthly` asking for its period total should get its month. The
    field names keep the `weekly_` prefix because that is the contract the
    consumer already has; `period_start`/`period_end` state what the window
    actually was so the caller is never guessing.
    """
    await require_access(db, membership)
    anchor = anchor or _today_kst()
    config = await read_family_config(db, family_id, membership)
    period_start, period_end = _period_for(config["cycle_type"], anchor)

    balance = await _projection(db, family_id, membership.id)
    remaining = (
        await db.execute(
            select(func.count())
            .select_from(MarkpointMission)
            .where(
                MarkpointMission.family_group_id == family_id,
                MarkpointMission.assignee_membership_id == membership.id,
                MarkpointMission.scheduled_for.between(period_start, period_end),
                MarkpointMission.status.in_(("active", "pending_approval")),
            )
        )
    ).scalar_one()
    expected = (
        await db.execute(
            select(func.coalesce(func.sum(MarkpointMission.reward_amount), 0)).where(
                MarkpointMission.family_group_id == family_id,
                MarkpointMission.assignee_membership_id == membership.id,
                MarkpointMission.scheduled_for.between(period_start, period_end),
                MarkpointMission.status.in_(("active", "pending_approval")),
            )
        )
    ).scalar_one()

    return {
        "family_group_id": family_id,
        "family_membership_id": membership.id,
        "cycle_type": config["cycle_type"],
        "period_start": period_start,
        "period_end": period_end,
        "today": anchor,
        "today_earned": await _sum_ledger(db, family_id, membership.id, positive=True, start=anchor, end=anchor),
        "today_deducted": await _sum_ledger(db, family_id, membership.id, positive=False, start=anchor, end=anchor),
        "weekly_earned": await _sum_ledger(db, family_id, membership.id, positive=True, start=period_start, end=period_end),
        "weekly_deducted": await _sum_ledger(db, family_id, membership.id, positive=False, start=period_start, end=period_end),
        "current_balance": balance.current_balance,
        "lifetime_earned": balance.lifetime_earned,
        "lifetime_spent": balance.lifetime_spent,
        "remaining_missions": int(remaining),
        "expected_points": int(expected),
    }


async def own_weekly_detail(db: AsyncSession, family_id: int, membership: FamilyMembership, anchor: date | None = None) -> dict:
    """Per-date Mission breakdown for the current cycle period.

    Returned as one entry per date rather than a flat list so the Wave 6 UI can
    render a calendar without regrouping, and so an empty day is explicit
    rather than inferred from a gap.
    """
    await require_access(db, membership)
    anchor = anchor or _today_kst()
    config = await read_family_config(db, family_id, membership)
    period_start, period_end = _period_for(config["cycle_type"], anchor)

    missions = list(
        (
            await db.execute(
                select(MarkpointMission)
                .where(
                    MarkpointMission.family_group_id == family_id,
                    MarkpointMission.assignee_membership_id == membership.id,
                    MarkpointMission.scheduled_for.between(period_start, period_end),
                )
                .order_by(MarkpointMission.scheduled_for, MarkpointMission.id)
            )
        ).scalars()
    )

    by_date: dict[date, list] = {}
    for mission in missions:
        by_date.setdefault(mission.scheduled_for, []).append(mission)

    # 1k/1s (W7.5 Phase C) need description/checklist/rejection_reason and a
    # resolved reviewer name per Mission. Resolved once per distinct reviewer
    # Membership, not once per Mission, so a period with many completed/
    # rejected Missions from the same admin does not repeat the same lookup.
    reviewer_ids = {m.approved_by_membership_id for m in missions if m.approved_by_membership_id}
    reviewer_names = {mid: await reviewer_display_name(db, mid) for mid in reviewer_ids}

    days = []
    cursor = period_start
    while cursor <= period_end:
        items = by_date.get(cursor, [])
        days.append(
            {
                "date": cursor,
                "missions": [
                    {
                        "id": m.id,
                        "title": m.title,
                        "status": m.status,
                        "reward_amount": m.reward_amount,
                        "template_id": m.template_id,
                        "description": m.description,
                        "checklist": m.checklist,
                        "rejection_reason": m.rejection_reason,
                        "reviewer_display_name": reviewer_names.get(m.approved_by_membership_id) or None,
                    }
                    for m in items
                ],
                "remaining": sum(1 for m in items if m.status in ("active", "pending_approval")),
                "completed": sum(1 for m in items if m.status == "completed"),
            }
        )
        cursor += timedelta(days=1)

    return {
        "family_group_id": family_id,
        "family_membership_id": membership.id,
        "cycle_type": config["cycle_type"],
        "period_start": period_start,
        "period_end": period_end,
        "days": days,
        "total_missions": len(missions),
        "remaining_missions": sum(1 for m in missions if m.status in ("active", "pending_approval")),
        "completed_missions": sum(1 for m in missions if m.status == "completed"),
        "expected_points": sum(m.reward_amount for m in missions if m.status in ("active", "pending_approval")),
        "earned_points": sum(m.reward_amount for m in missions if m.status == "completed"),
    }


# ===========================================================================
# MP-P03 — deduction history and append-only correction
# ===========================================================================


async def deduction_history(db: AsyncSession, family_id: int, membership: FamilyMembership) -> list[dict]:
    """Every debit for this member, with its correction lineage.

    `reversal_of_entry_id` is what makes a correction traceable: the reversal
    points at the debit it undoes and the replacement carries the same source,
    so "what was this changed from, and by whom" is answerable from the rows
    themselves rather than from an audit log that could be pruned.
    """
    await require_access(db, membership)
    rows = list(
        (
            await db.execute(
                select(MarkpointLedgerEntry)
                .where(
                    MarkpointLedgerEntry.family_group_id == family_id,
                    MarkpointLedgerEntry.family_membership_id == membership.id,
                    MarkpointLedgerEntry.entry_type.in_(("MANUAL_DEBIT", "REVERSAL", "CORRECTION")),
                )
                .order_by(MarkpointLedgerEntry.id)
            )
        ).scalars()
    )
    reversed_ids = {r.reversal_of_entry_id for r in rows if r.reversal_of_entry_id is not None}
    return [
        {
            "id": r.id,
            "amount": r.amount,
            "entry_type": r.entry_type,
            "reason": r.reason,
            "reversal_of_entry_id": r.reversal_of_entry_id,
            "corrected": r.id in reversed_ids,
            "occurred_at": r.occurred_at,
            "created_by_membership_id": r.created_by_membership_id,
        }
        for r in rows
    ]


async def correct_deduction(
    db: AsyncSession,
    family_id: int,
    actor: FamilyMembership,
    *,
    entry_id: int,
    new_amount: int | None,
    reason: str,
) -> dict:
    """Correct a debit by reversing it and, optionally, replacing it.

    The Ledger is append-only, so a correction is **two new rows**, never an
    edit:

        original debit   -100   (untouched, forever)
        reversal         +100   reversal_of_entry_id -> original
        replacement       -80   (only when new_amount is given)

    Editing the original in place would be simpler and is exactly what must not
    happen: the balance would change with no record of why, and any report
    already rendered from the old value would become unreproducible.

    `new_amount=None` cancels the deduction outright — reversal only. Both rows
    commit in one transaction, so a balance can never be seen with the reversal
    applied but not its replacement.
    """
    await require_permission(db, actor, POINTS_ADJUST)
    original = (
        await db.execute(
            select(MarkpointLedgerEntry).where(
                MarkpointLedgerEntry.id == entry_id,
                MarkpointLedgerEntry.family_group_id == family_id,
            )
        )
    ).scalars().first()
    # 404 rather than 403 for a foreign entry: confirming that an id exists in
    # another Family is itself a disclosure.
    if original is None:
        raise HTTPException(status_code=404, detail="차감 내역을 찾을 수 없습니다")
    if original.entry_type != "MANUAL_DEBIT" or original.amount >= 0:
        raise HTTPException(status_code=409, detail="차감 항목이 아닙니다")
    if new_amount is not None and new_amount >= 0:
        raise HTTPException(status_code=422, detail="정정 차감액은 음수여야 합니다")
    if not reason:
        raise HTTPException(status_code=422, detail="정정 사유가 필요합니다")

    already = (
        await db.execute(
            select(func.count())
            .select_from(MarkpointLedgerEntry)
            .where(
                MarkpointLedgerEntry.family_group_id == family_id,
                MarkpointLedgerEntry.reversal_of_entry_id == original.id,
            )
        )
    ).scalar_one()
    if already:
        raise HTTPException(status_code=409, detail="이미 정정된 차감 내역입니다")

    reversal, _ = await _entry(
        db,
        family_id=family_id,
        member_id=original.family_membership_id,
        amount=-original.amount,
        entry_type="REVERSAL",
        source_type="deduction_correction",
        source_identifier=str(original.id),
        idempotency_key=f"deduction-reversal:{original.id}",
        actor_id=actor.id,
        reason=reason,
        reversal_of=original.id,
    )

    replacement = None
    if new_amount is not None:
        replacement, _ = await _entry(
            db,
            family_id=family_id,
            member_id=original.family_membership_id,
            amount=new_amount,
            entry_type="MANUAL_DEBIT",
            source_type="deduction_replacement",
            source_identifier=str(original.id),
            idempotency_key=f"deduction-replacement:{original.id}",
            actor_id=actor.id,
            reason=reason,
        )

    _audit(
        db,
        family_id,
        actor.id,
        "deduction.corrected",
        "ledger_entry",
        str(original.id),
        {"reversal_id": reversal.id, "replacement_id": replacement.id if replacement else None, "new_amount": new_amount},
    )
    await db.commit()
    return {
        "original_entry_id": original.id,
        "original_amount": original.amount,
        "reversal_entry_id": reversal.id,
        "replacement_entry_id": replacement.id if replacement else None,
        "new_amount": new_amount,
    }


# ===========================================================================
# MP-A01 — admin mission filters and bulk approval
# ===========================================================================


async def admin_list_missions(
    db: AsyncSession,
    family_id: int,
    actor: FamilyMembership,
    *,
    assignee_membership_id: int | None = None,
    mission_status: str | None = None,
    template_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 200,
) -> list[MarkpointMission]:
    """Filtered mission list for a service administrator.

    `family_group_id` is applied unconditionally and is not one of the optional
    filters — a caller cannot widen the query to another Family by omitting a
    parameter, which is the usual way this kind of endpoint leaks.
    """
    await require_permission(db, actor, MISSION_MANAGE)
    stmt = select(MarkpointMission).where(MarkpointMission.family_group_id == family_id)
    if assignee_membership_id is not None:
        stmt = stmt.where(MarkpointMission.assignee_membership_id == assignee_membership_id)
    if mission_status is not None:
        stmt = stmt.where(MarkpointMission.status == mission_status)
    if template_id is not None:
        stmt = stmt.where(MarkpointMission.template_id == template_id)
    if date_from is not None:
        stmt = stmt.where(MarkpointMission.scheduled_for >= date_from)
    if date_to is not None:
        stmt = stmt.where(MarkpointMission.scheduled_for <= date_to)
    stmt = stmt.order_by(MarkpointMission.scheduled_for.desc(), MarkpointMission.id.desc()).limit(
        max(1, min(int(limit), 500))
    )
    return list((await db.execute(stmt)).scalars())


async def bulk_approve_missions(
    db: AsyncSession, family_id: int, actor: FamilyMembership, mission_ids: list[int]
) -> dict:
    """Approve an explicit list of missions in one transaction.

    **All-or-nothing.** No approved contract defines partial-success semantics,
    so inventing them would be inventing policy — and a half-applied batch is
    the harder failure to reason about afterwards, because the caller cannot
    tell from the balance which half landed. Any ineligible mission raises and
    the whole transaction rolls back; the response names the offender.

    Each reward still goes through the same idempotent `_entry` path as a
    single approve, so a mission already approved by a concurrent single-approve
    contributes no second reward — it is simply already `completed` and is
    counted as skipped.
    """
    await require_permission(db, actor, MISSION_MANAGE)
    if not mission_ids:
        raise HTTPException(status_code=422, detail="승인할 미션 ID가 필요합니다")
    unique_ids = list(dict.fromkeys(mission_ids))

    rows = list(
        (
            await db.execute(
                select(MarkpointMission)
                .where(
                    MarkpointMission.id.in_(unique_ids),
                    MarkpointMission.family_group_id == family_id,
                )
                .order_by(MarkpointMission.id)
                .with_for_update()
            )
        ).scalars()
    )
    found = {m.id for m in rows}
    missing = [i for i in unique_ids if i not in found]
    if missing:
        # Includes ids that exist in another Family — reported as not found so
        # the response never confirms a foreign mission's existence.
        raise HTTPException(status_code=404, detail=f"미션을 찾을 수 없습니다: {missing}")

    ineligible = [m.id for m in rows if m.status not in ("pending_approval", "completed")]
    if ineligible:
        raise HTTPException(
            status_code=409,
            detail=f"승인할 수 없는 상태의 미션이 포함되어 있습니다: {ineligible}",
        )

    approved, skipped = [], []
    for mission in rows:
        if mission.status == "completed":
            skipped.append(mission.id)
            continue
        await _member(db, family_id, mission.assignee_membership_id)
        entry, inserted = await _entry(
            db,
            family_id=family_id,
            member_id=mission.assignee_membership_id,
            amount=mission.reward_amount,
            entry_type="MISSION_REWARD",
            source_type="mission_approval",
            source_identifier=str(mission.id),
            idempotency_key=f"mission-approved:{mission.id}",
            actor_id=actor.id,
        )
        mission.status = "completed"
        mission.approved_by_membership_id = actor.id
        mission.completed_at = _now()
        if inserted:
            await outbox_service.enqueue_event(
                db,
                owner_service=SERVICE_CODE,
                event_type="mission.approved",
                event_version=1,
                aggregate_type="mission",
                aggregate_id=str(mission.id),
                source_event_id=f"mission-approved:{mission.id}",
                family_id=family_id,
                payload={
                    "family_group_id": family_id,
                    "mission_id": mission.id,
                    "assignee_membership_id": mission.assignee_membership_id,
                    "reward_amount": mission.reward_amount,
                },
            )
        approved.append(mission.id)

    _audit(
        db,
        family_id,
        actor.id,
        "mission.bulk_approved",
        "mission",
        ",".join(str(i) for i in approved) or "none",
        {"approved": approved, "skipped_already_completed": skipped},
    )
    await db.commit()
    return {
        "requested": len(unique_ids),
        "approved": approved,
        "skipped_already_completed": skipped,
    }

async def list_audit_events(db: AsyncSession, family_id: int, limit: int = 100) -> list[MarkpointAuditEvent]:
    """Read-only, for `family_activity_log`'s own Slice (2r) -- moved here
    from that domain's own service so it reaches this table through this
    module's dotted reference rather than importing `MarkpointAuditEvent`
    directly, per the Backend Guide's no-direct-cross-domain-DB-access rule."""
    stmt = (
        select(MarkpointAuditEvent)
        .where(MarkpointAuditEvent.family_group_id == family_id)
        .order_by(MarkpointAuditEvent.created_at.desc())
        .limit(limit)
    )
    return list((await db.execute(stmt)).scalars())

async def search_missions_by_title(db: AsyncSession, family_id: int, query: str) -> list[MarkpointMission]:
    """Read-only, for `family_search`'s own Slice (3j) -- same
    dotted-reference reasoning as `list_audit_events` above."""
    stmt = (
        select(MarkpointMission)
        .where(MarkpointMission.family_group_id == family_id, MarkpointMission.title.ilike(f"%{query}%"))
        .order_by(MarkpointMission.scheduled_for.desc())
    )
    return list((await db.execute(stmt)).scalars())
