"""Family Rules application service. Read needs only active Membership
(already enforced by `get_family_membership`); replacing the whole list
needs `FAMILY_MEMBERS_MANAGE` -- parent-authored rules, not a general
member capability."""
from __future__ import annotations
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.family.models import FamilyMembership
from .models import FamilyRule


async def list_rules(db: AsyncSession, family_id: int) -> list[FamilyRule]:
    stmt = select(FamilyRule).where(FamilyRule.family_group_id == family_id).order_by(FamilyRule.category, FamilyRule.sort_order, FamilyRule.id)
    return list((await db.execute(stmt)).scalars())


async def replace_rules(db: AsyncSession, family_id: int, actor: FamilyMembership, entries: list[dict]) -> list[FamilyRule]:
    """Permission (`FAMILY_MEMBERS_MANAGE`) is enforced by the router's
    `require_family_permission` dependency before this runs."""
    await db.execute(delete(FamilyRule).where(FamilyRule.family_group_id == family_id))
    rows = [
        FamilyRule(
            family_group_id=family_id,
            category=entry["category"],
            label=entry["label"],
            value_text=entry["value_text"],
            sort_order=index,
            updated_by_membership_id=actor.id,
        )
        for index, entry in enumerate(entries)
    ]
    db.add_all(rows)
    await db.commit()
    return await list_rules(db, family_id)
