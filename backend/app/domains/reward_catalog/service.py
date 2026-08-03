"""Reward Catalog application service. Catalog management (create/update)
needs `MISSION_MANAGE` -- the same manager role that already governs
Mission creation, since reward rules are a parent/admin product decision
like missions are. Reading and redeeming need only Markpoint access
(`require_access`), same boundary every `own_*` Markpoint read uses.

Redemption reuses `markpoint_target.service.self_spend` for the point-debit
side rather than duplicating Ledger logic -- see that function's own
docstring for why it exists instead of reusing `adjust_points`.
"""
from __future__ import annotations
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family.models import FamilyMembership
from app.domains.markpoint_target import service as markpoint_service
from .models import RewardCatalogItem, RewardRedemption


async def list_rewards(db: AsyncSession, family_id: int, actor: FamilyMembership) -> list[RewardCatalogItem]:
    await markpoint_service.require_access(db, actor)
    stmt = select(RewardCatalogItem).where(RewardCatalogItem.family_group_id == family_id).order_by(RewardCatalogItem.cost)
    return list((await db.execute(stmt)).scalars())


async def create_reward(db: AsyncSession, family_id: int, actor: FamilyMembership, *, name: str, cost: int) -> RewardCatalogItem:
    await markpoint_service.require_permission(db, actor, markpoint_service.MISSION_MANAGE)
    reward = RewardCatalogItem(family_group_id=family_id, created_by_membership_id=actor.id, name=name, cost=cost)
    db.add(reward)
    await db.commit()
    await db.refresh(reward)
    return reward


async def _get_reward(db: AsyncSession, family_id: int, reward_id: int) -> RewardCatalogItem:
    reward = await db.get(RewardCatalogItem, reward_id)
    if reward is None or reward.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="보상을 찾을 수 없습니다")
    return reward


async def update_reward(db: AsyncSession, family_id: int, actor: FamilyMembership, reward_id: int, updates: dict) -> RewardCatalogItem:
    await markpoint_service.require_permission(db, actor, markpoint_service.MISSION_MANAGE)
    reward = await _get_reward(db, family_id, reward_id)
    for key, value in updates.items():
        if value is not None:
            setattr(reward, key, value)
    await db.commit()
    await db.refresh(reward)
    return reward


async def redeem_reward(db: AsyncSession, family_id: int, actor: FamilyMembership, reward_id: int, idempotency_key: str) -> RewardRedemption:
    reward = await _get_reward(db, family_id, reward_id)
    if not reward.is_available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="교환할 수 없는 보상입니다")

    entry = await markpoint_service.self_spend(
        db, family_id, actor, -reward.cost, f"보상 교환: {reward.name}",
        source_type="reward_redemption", source_identifier=f"reward:{reward_id}:{idempotency_key}",
        idempotency_key=f"reward-redeem:{family_id}:{actor.id}:{reward_id}:{idempotency_key}",
    )

    # `self_spend` is idempotent on its own key: a retried request resolves
    # to the same Ledger entry. Look up by that entry id, not "most recent
    # redemption for this reward", so a genuinely separate second redemption
    # of the same reward is never mistaken for a retry of the first.
    existing = (
        await db.execute(select(RewardRedemption).where(RewardRedemption.ledger_entry_id == entry.id))
    ).scalars().first()
    if existing is not None:
        return existing

    redemption = RewardRedemption(
        family_group_id=family_id, reward_item_id=reward_id, redeemed_by_membership_id=actor.id,
        cost_at_redemption=reward.cost, ledger_entry_id=entry.id,
    )
    db.add(redemption)
    await db.commit()
    await db.refresh(redemption)
    return redemption
