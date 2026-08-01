from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_current_account, get_family_membership
from app.domains.family.models import Account, FamilyMembership
from app.domains.family import service as family_service
from . import service
from .schemas import (
    BalanceOut, BulkApproval, CycleConfigOut, CycleConfigUpdate, DeductionCorrection,
    LedgerOut, LevelOut, MissionCreate, MissionDecision, MissionOut, PointAdjustment,
    TemplateCreate, TemplateOut, TemplateUpdate,
)

router=APIRouter(tags=["markpoint"])

async def _me(family_id:int, account:Account=Depends(get_current_account), db:AsyncSession=Depends(get_db)):
    return await family_service.get_active_membership(db, account.id, family_id)

@router.post("/api/families/{family_id}/markpoint/missions", response_model=MissionOut, status_code=status.HTTP_201_CREATED)
async def create(family_id:int, body:MissionCreate, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.create_mission(db, family_id, actor, assignee_id=body.assignee_membership_id, title=body.title, scheduled_for=body.scheduled_for, reward_amount=body.reward_amount)

@router.post("/api/families/{family_id}/markpoint/missions/{mission_id}/submit", response_model=MissionOut)
async def submit(family_id:int, mission_id:int, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.submit_mission(db, family_id, actor, mission_id)

@router.post("/api/families/{family_id}/markpoint/missions/{mission_id}/approve", response_model=MissionOut)
async def approve(family_id:int, mission_id:int, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.approve_mission(db, family_id, actor, mission_id)

@router.post("/api/families/{family_id}/markpoint/missions/{mission_id}/reverse", response_model=MissionOut)
async def reverse(family_id:int, mission_id:int, body:MissionDecision, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.reverse_mission_reward(db, family_id, actor, mission_id, body.reason or "reversed")

@router.post("/api/families/{family_id}/markpoint/missions/{mission_id}/reject", response_model=MissionOut)
async def reject(family_id:int, mission_id:int, body:MissionDecision, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.reject_mission(db,family_id,actor,mission_id,body.reason)

@router.post("/api/families/{family_id}/markpoint/missions/{mission_id}/cancel", response_model=MissionOut)
async def cancel(family_id:int, mission_id:int, body:MissionDecision, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.cancel_mission(db,family_id,actor,mission_id,body.reason or "cancelled")

@router.post("/api/families/{family_id}/markpoint/missions/expire")
async def expire(family_id:int, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return {"expired":await service.expire_stale_missions(db,family_id,actor)}

@router.get("/api/families/{family_id}/markpoint/templates",response_model=list[TemplateOut])
async def templates(family_id:int,actor:FamilyMembership=Depends(get_family_membership),db:AsyncSession=Depends(get_db)): return await service.list_templates(db,family_id,actor)
@router.post("/api/families/{family_id}/markpoint/templates",response_model=TemplateOut,status_code=201)
async def template_create(family_id:int,body:TemplateCreate,actor:FamilyMembership=Depends(get_family_membership),db:AsyncSession=Depends(get_db)): return await service.create_template(db,family_id,actor,assignee_id=body.assignee_membership_id,title=body.title,reward_amount=body.reward_amount,cycle_type=body.cycle_type,start_date=body.start_date,end_date=body.end_date,day_of_week=body.day_of_week)
@router.patch("/api/families/{family_id}/markpoint/templates/{template_id}",response_model=TemplateOut)
async def template_patch(family_id:int,template_id:int,body:TemplateUpdate,actor:FamilyMembership=Depends(get_family_membership),db:AsyncSession=Depends(get_db)): return await service.update_template(db,family_id,actor,template_id,body.model_dump(exclude_unset=True))
@router.delete("/api/families/{family_id}/markpoint/templates/{template_id}",response_model=TemplateOut)
async def template_deactivate(family_id:int,template_id:int,actor:FamilyMembership=Depends(get_family_membership),db:AsyncSession=Depends(get_db)): return await service.deactivate_template(db,family_id,actor,template_id)
@router.post("/api/families/{family_id}/markpoint/templates/{template_id}/materialize",response_model=MissionOut)
async def materialize(family_id:int,template_id:int,scheduled_for:__import__('datetime').date=__import__('fastapi').Query(...),actor:FamilyMembership=Depends(get_family_membership),db:AsyncSession=Depends(get_db)): return await service.materialize_template(db,family_id,actor,template_id,scheduled_for)

@router.post("/api/families/{family_id}/markpoint/ledger/adjustments", response_model=LedgerOut, status_code=status.HTTP_201_CREATED)
async def adjustment(family_id:int, body:PointAdjustment, actor:FamilyMembership=Depends(get_family_membership), db:AsyncSession=Depends(get_db)):
    return await service.adjust_points(db, family_id, actor, body.beneficiary_membership_id, body.amount, body.reason, body.idempotency_key)

@router.get("/api/me/markpoint/missions", response_model=list[MissionOut])
async def my_missions(family_id:int, membership:FamilyMembership=Depends(_me), db:AsyncSession=Depends(get_db)):
    return await service.own_missions(db, family_id, membership)

@router.get("/api/me/markpoint/ledger", response_model=list[LedgerOut])
async def my_ledger(family_id:int, membership:FamilyMembership=Depends(_me), db:AsyncSession=Depends(get_db)):
    return await service.own_ledger(db, family_id, membership)

@router.get("/api/me/markpoint/balance", response_model=BalanceOut)
async def my_balance(family_id:int, membership:FamilyMembership=Depends(_me), db:AsyncSession=Depends(get_db)):
    return await service.own_balance(db, family_id, membership)

@router.get("/api/me/markpoint/level", response_model=LevelOut)
async def my_level(family_id:int, membership:FamilyMembership=Depends(_me), db:AsyncSession=Depends(get_db)):
    balance, info=await service.own_level(db, family_id, membership)
    return LevelOut(family_group_id=family_id, family_membership_id=membership.id, lifetime_earned=balance.lifetime_earned, level=info.level, title=info.title, current_threshold=info.current_threshold, next_threshold=info.next_threshold, progress_percent=info.progress_percent)

@router.get("/api/me/markpoint/summary")
async def my_summary(family_id:int,membership:FamilyMembership=Depends(_me),db:AsyncSession=Depends(get_db)): return await service.own_summary(db,family_id,membership)

@router.get("/api/me/markpoint/deductions",response_model=list[LedgerOut])
async def my_deductions(family_id:int,membership:FamilyMembership=Depends(_me),db:AsyncSession=Depends(get_db)):
    return [row for row in await service.own_ledger(db,family_id,membership) if row.amount<0]


# ---------------------------------------------------------------------------
# MP-S04 — per-Family cycle configuration
# ---------------------------------------------------------------------------
# Family-scoped, so it sits under `/api/families/{family_id}/markpoint/...`
# alongside the rest of the service. Reading needs Markpoint access only;
# writing needs `markpoint.missions.manage`, which no FAMILY-scope role carries
# (migration 0006) — being the family owner is deliberately not enough.


@router.get("/api/families/{family_id}/markpoint/config", response_model=CycleConfigOut)
async def read_config(
    family_id: int,
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    return await service.read_family_config(db, family_id, actor)


@router.put("/api/families/{family_id}/markpoint/config", response_model=CycleConfigOut)
async def update_config(
    family_id: int,
    body: CycleConfigUpdate,
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_family_config(
        db, family_id, actor, cycle_type=body.cycle_type, display_name=body.display_name
    )


# ---------------------------------------------------------------------------
# MP-M03 — rolling materialization
# ---------------------------------------------------------------------------


@router.post("/api/families/{family_id}/markpoint/templates/materialize-window")
async def materialize_window(
    family_id: int,
    template_id: int | None = Query(default=None),
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    """Generate the rolling window's missions for one Template or all active ones."""
    return await service.materialize_rolling_window(db, family_id, actor, template_id=template_id)


# ---------------------------------------------------------------------------
# MP-M04 / MP-P02 — weekly detail and projection
# ---------------------------------------------------------------------------


@router.get("/api/me/markpoint/weekly")
async def my_weekly(
    family_id: int,
    membership: FamilyMembership = Depends(_me),
    db: AsyncSession = Depends(get_db),
):
    return await service.own_weekly_detail(db, family_id, membership)


@router.get("/api/me/markpoint/projection")
async def my_projection(
    family_id: int,
    membership: FamilyMembership = Depends(_me),
    db: AsyncSession = Depends(get_db),
):
    return await service.own_projection(db, family_id, membership)


# ---------------------------------------------------------------------------
# MP-P03 — deduction history and correction
# ---------------------------------------------------------------------------


@router.get("/api/me/markpoint/deductions/history")
async def my_deduction_history(
    family_id: int,
    membership: FamilyMembership = Depends(_me),
    db: AsyncSession = Depends(get_db),
):
    return await service.deduction_history(db, family_id, membership)


@router.post("/api/families/{family_id}/markpoint/ledger/{entry_id}/correct")
async def correct_deduction(
    family_id: int,
    entry_id: int,
    body: DeductionCorrection,
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    """Reverse a debit and optionally replace it. The Ledger is append-only:
    this writes new rows and never edits the original."""
    return await service.correct_deduction(
        db, family_id, actor, entry_id=entry_id, new_amount=body.new_amount, reason=body.reason
    )


# ---------------------------------------------------------------------------
# MP-A01 — admin filters and bulk approval
# ---------------------------------------------------------------------------


@router.get("/api/families/{family_id}/markpoint/missions", response_model=list[MissionOut])
async def admin_missions(
    family_id: int,
    assignee_membership_id: int | None = Query(default=None),
    mission_status: str | None = Query(default=None),
    template_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    return await service.admin_list_missions(
        db,
        family_id,
        actor,
        assignee_membership_id=assignee_membership_id,
        mission_status=mission_status,
        template_id=template_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@router.post("/api/families/{family_id}/markpoint/missions/bulk-approve")
async def bulk_approve(
    family_id: int,
    body: BulkApproval,
    actor: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    """All-or-nothing. No approved contract defines partial success, so an
    ineligible mission rolls the whole batch back rather than leaving a
    half-applied balance."""
    return await service.bulk_approve_missions(db, family_id, actor, body.mission_ids)
