#!/usr/bin/env python3
"""Create explicit synthetic Phase 1 mappings in an isolated database only.

This is not an operating migration tool.  It deliberately uses known synthetic
legacy IDs and never guesses names, usernames, relationships, or owners.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete, select

from app.database import AsyncSessionLocal
from app.domains.family.models import (
    Account, FamilyGroup, FamilyMembership, LegacyIdentityMapping,
    MembershipRoleAssignment, Role, ServiceSubscription,
)


async def role(db, scope_type: str, code: str, service_code=None):
    stmt = select(Role).where(Role.scope_type == scope_type, Role.code == code)
    if service_code is None:
        stmt = stmt.where(Role.service_code.is_(None))
    else:
        stmt = stmt.where(Role.service_code == service_code)
    return (await db.execute(stmt)).scalars().one()


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for model in (MembershipRoleAssignment, LegacyIdentityMapping, ServiceSubscription, FamilyMembership, FamilyGroup, Account):
            await db.execute(delete(model))
        await db.commit()

        accounts = {
            "owner_a": Account(display_name="Synthetic Owner A"),
            "owner_b": Account(display_name="Synthetic Owner B"),
            "other": Account(display_name="Synthetic Other Family Member"),
            "admin": Account(display_name="Synthetic Legacy Admin"),
            "participant": Account(display_name="Synthetic Service Participant"),
            "suspended": Account(display_name="Synthetic Suspended", status="suspended"),
        }
        db.add_all(accounts.values())
        await db.flush()
        alpha = FamilyGroup(name="Synthetic Family Alpha")
        beta = FamilyGroup(name="Synthetic Family Beta")
        db.add_all((alpha, beta))
        await db.flush()
        now = datetime.now(timezone.utc)
        memberships = {
            "owner_a": FamilyMembership(family_group_id=alpha.id, account_id=accounts["owner_a"].id, relationship="other", status="active", joined_at=now),
            "owner_b": FamilyMembership(family_group_id=alpha.id, account_id=accounts["owner_b"].id, relationship="other", status="active", joined_at=now),
            "admin": FamilyMembership(family_group_id=alpha.id, account_id=accounts["admin"].id, relationship="other", status="active", joined_at=now),
            "participant": FamilyMembership(family_group_id=alpha.id, account_id=accounts["participant"].id, relationship="other", status="active", joined_at=now),
            "owner_a_beta": FamilyMembership(family_group_id=beta.id, account_id=accounts["owner_a"].id, relationship="other", status="active", joined_at=now),
            "other": FamilyMembership(family_group_id=beta.id, account_id=accounts["other"].id, relationship="other", status="active", joined_at=now),
        }
        db.add_all(memberships.values())
        await db.flush()
        owner_role = await role(db, "FAMILY", "owner")
        admin_role = await role(db, "FAMILY", "admin")
        member_role = await role(db, "FAMILY", "member")
        participant_role = await role(db, "SERVICE", "participant", "markpoint")
        db.add_all((
            MembershipRoleAssignment(membership_id=memberships["owner_a"].id, role_id=owner_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["owner_b"].id, role_id=owner_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["admin"].id, role_id=admin_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["participant"].id, role_id=participant_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["owner_a_beta"].id, role_id=member_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["other"].id, role_id=member_role.id, assigned_by_account_id=accounts["other"].id),
        ))
        db.add_all((
            ServiceSubscription(family_group_id=alpha.id, service_code="markpoint", status="active", started_at=now),
            ServiceSubscription(family_group_id=beta.id, service_code="markpoint", status="cancelled", ended_at=now),
        ))
        db.add_all((
            LegacyIdentityMapping(account_id=accounts["owner_a"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="1", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["owner_b"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="2", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["other"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="3", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["participant"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="4", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["admin"].id, legacy_system="markpoint", legacy_identity_type="admin_auth", legacy_identity_id="1", mapping_status="linked"),
            LegacyIdentityMapping(account_id=None, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="999", mapping_status="ambiguous"),
        ))
        await db.commit()
        print("PHASE1_SYNTHETIC_SEED_OK")


if __name__ == "__main__":
    asyncio.run(main())
