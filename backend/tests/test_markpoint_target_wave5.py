"""Wave 5 Target Mission/Ledger integration tests against isolated PostgreSQL."""
from datetime import date, datetime, timezone
import asyncio
import pytest
from sqlalchemy import text, select
from sqlalchemy.exc import DBAPIError
from app.domains.family.models import Account, FamilyGroup, FamilyMembership, MembershipRoleAssignment, ServiceSubscription
from app.domains.markpoint_target import service
from app.domains.markpoint_target.models import MarkpointBalanceProjection, MarkpointLedgerEntry, MarkpointMission

async def _member(db, family_id, name):
    account=Account(display_name=name,status="active"); db.add(account); await db.flush()
    member=FamilyMembership(family_group_id=family_id,account_id=account.id,relationship="unknown",status="active",joined_at=datetime.now(timezone.utc)); db.add(member); await db.flush(); return member

async def _family(db):
    f=FamilyGroup(name="wave5",status="active"); db.add(f); await db.flush()
    db.add(ServiceSubscription(family_group_id=f.id,service_code="markpoint",status="active",started_at=datetime.now(timezone.utc))); await db.flush(); return f

async def _grant(db, member, code):
    role=(await db.execute(text("SELECT id FROM roles WHERE scope_type='SERVICE' AND service_code='markpoint' AND code=:code"),{"code":code})).scalar_one(); db.add(MembershipRoleAssignment(membership_id=member.id,role_id=role)); await db.commit()

@pytest.mark.asyncio
async def test_mission_approval_is_single_ledger_balance_and_outbox(db):
    family=await _family(db); manager=await _member(db,family.id,"manager"); child=await _member(db,family.id,"child"); await _grant(db,manager,"mission_manager")
    mission=await service.create_mission(db,family.id,manager,assignee_id=child.id,title="clean",scheduled_for=date.today(),reward_amount=11)
    await service.submit_mission(db,family.id,child,mission.id)
    await service.approve_mission(db,family.id,manager,mission.id)
    await service.approve_mission(db,family.id,manager,mission.id)
    entries=list((await db.execute(select(MarkpointLedgerEntry))).scalars()); assert len(entries)==1 and entries[0].amount==11
    balance=(await db.execute(select(MarkpointBalanceProjection))).scalars().one(); assert (balance.current_balance,balance.lifetime_earned)==(11,11)
    assert (await db.execute(text("SELECT count(*) FROM service_outbox_events WHERE owner_service='markpoint' AND event_type='mission.approved'"))).scalar_one()==1

@pytest.mark.asyncio
async def test_reversal_is_append_only_and_only_once(db):
    family=await _family(db); manager=await _member(db,family.id,"manager"); child=await _member(db,family.id,"child"); await _grant(db,manager,"mission_manager")
    mission=await service.create_mission(db,family.id,manager,assignee_id=child.id,title="clean",scheduled_for=date.today(),reward_amount=7); await service.submit_mission(db,family.id,child,mission.id); await service.approve_mission(db,family.id,manager,mission.id); await service.reverse_mission_reward(db,family.id,manager,mission.id,"wrong")
    entries=list((await db.execute(select(MarkpointLedgerEntry).order_by(MarkpointLedgerEntry.id))).scalars()); assert [x.amount for x in entries]==[7,-7]
    with pytest.raises(Exception): await service.reverse_mission_reward(db,family.id,manager,mission.id,"again")
    await db.rollback()
    async with db.begin():
        with pytest.raises(Exception): await db.execute(text("UPDATE markpoint_ledger_entries SET amount=99 WHERE id=:id"),{"id":entries[0].id})

@pytest.mark.asyncio
async def test_manual_adjustment_is_idempotent_and_cross_family_is_rejected(db):
    family=await _family(db); manager=await _member(db,family.id,"manager"); child=await _member(db,family.id,"child"); await _grant(db,manager,"point_admin")
    first=await service.adjust_points(db,family.id,manager,child.id,5,"bonus","k1"); second=await service.adjust_points(db,family.id,manager,child.id,5,"bonus","k1"); assert first.id==second.id
    other=await _family(db); outsider=await _member(db,other.id,"outsider")
    with pytest.raises(Exception): await service.adjust_points(db,family.id,manager,outsider.id,5,"no","k2")

@pytest.mark.asyncio
async def test_concurrent_approval_has_one_reward(db):
    family=await _family(db); manager=await _member(db,family.id,"manager"); child=await _member(db,family.id,"child"); await _grant(db,manager,"mission_manager")
    mission=await service.create_mission(db,family.id,manager,assignee_id=child.id,title="same",scheduled_for=date.today(),reward_amount=3); await service.submit_mission(db,family.id,child,mission.id)
    # separate sessions exercise the row lock/unique idempotency boundary.
    from app.database import AsyncSessionLocal
    async def run_one():
        async with AsyncSessionLocal() as s:
            actor=await s.get(FamilyMembership,manager.id); return await service.approve_mission(s,family.id,actor,mission.id)
    results=await asyncio.gather(run_one(),run_one(),return_exceptions=True); assert sum(not isinstance(x,Exception) for x in results)>=1
    rows=list((await db.execute(select(MarkpointLedgerEntry).where(MarkpointLedgerEntry.source_identifier==str(mission.id)))).scalars()); assert len(rows)==1
