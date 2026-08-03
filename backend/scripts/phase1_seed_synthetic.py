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
    Account, AccountCredential, AccountSession, FamilyGroup, FamilyMembership,
    LegacyIdentityMapping, MembershipRoleAssignment, Role, ServiceSubscription,
)
# MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001: Target fixture data. Wave 6
# journeys need an Account-native sign-in and real Markpoint/Wagle rows — the
# Target screens read the Target API, so a seed with only legacy mappings
# leaves every one of them empty.
from app.domains.family import auth_service
from app.domains.markpoint_target.models import (
    MarkpointMission, MarkpointMissionTemplate,
)
from app.domains.wagle.models import (
    WagleMessage, WagleParticipant, WagleParticipantReadState, WagleRoom,
)

# Synthetic only, and only ever loaded into an isolated database. Kept beside
# the seed rather than in the tests so both browsers in the two-context
# realtime journey sign in the same way the product does.
SEED_PASSWORD = "Synthetic!Pass9"



async def role(db, scope_type: str, code: str, service_code=None):
    stmt = select(Role).where(Role.scope_type == scope_type, Role.code == code)
    if service_code is None:
        stmt = stmt.where(Role.service_code.is_(None))
    else:
        stmt = stmt.where(Role.service_code == service_code)
    return (await db.execute(stmt)).scalars().one()


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for model in (
            MarkpointMission, MarkpointMissionTemplate,
            # WagleMessage cascades WagleMessageReaction (ondelete=CASCADE);
            # read-states and participants must go before their FK targets.
            WagleMessage, WagleParticipantReadState, WagleParticipant, WagleRoom,
            AccountSession, AccountCredential,
            MembershipRoleAssignment, LegacyIdentityMapping, ServiceSubscription,
            FamilyMembership, FamilyGroup, Account,
        ):
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
            # A FAMILY-scope role as well, so this membership carries
            # `family.read` and can open the Family home. Markpoint and Wagle
            # SERVICE roles grant nothing at the family level — that separation
            # is the point of D4, and without a FAMILY role a plain member is
            # correctly refused `/family` by its AccessBoundary.
            MembershipRoleAssignment(membership_id=memberships["participant"].id, role_id=member_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["owner_a_beta"].id, role_id=member_role.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["other"].id, role_id=member_role.id, assigned_by_account_id=accounts["other"].id),
        ))
        db.add_all((
            ServiceSubscription(family_group_id=alpha.id, service_code="markpoint", status="active", started_at=now),
            ServiceSubscription(family_group_id=beta.id, service_code="markpoint", status="cancelled", ended_at=now),
            # wagle.SERVICE_CODE (backend/app/domains/wagle/service.py) — without this row,
            # serviceStatus('wagle') on the frontend falls back to 'unavailable' and
            # /wagle always renders its disabled empty-state instead of the Room
            # List, regardless of Family/Membership/permission state.
            ServiceSubscription(family_group_id=alpha.id, service_code="wagle", status="active", started_at=now),
        ))
        db.add_all((
            LegacyIdentityMapping(account_id=accounts["owner_a"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="1", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["owner_b"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="2", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["other"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="3", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["participant"].id, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="4", mapping_status="linked"),
            LegacyIdentityMapping(account_id=accounts["admin"].id, legacy_system="markpoint", legacy_identity_type="admin_auth", legacy_identity_id="1", mapping_status="linked"),
            LegacyIdentityMapping(account_id=None, legacy_system="markpoint", legacy_identity_type="player_auth", legacy_identity_id="999", mapping_status="ambiguous"),
        ))
        # --- Target fixtures (Wave 6) -----------------------------------
        # Account credentials, so the browser can obtain an Account Session.
        # Usernames are stable and documented in the E2E spec; the password is
        # the synthetic constant above.
        for key, username in (
            ("owner_a", "owner.a"),      # Family A owner + Markpoint mission manager
            ("admin", "admin.a"),        # Family A Markpoint point admin
            ("participant", "member.a"), # Family A plain member
            ("other", "member.b"),       # Family B only
        ):
            await auth_service.create_credential(db, accounts[key].id, username, SEED_PASSWORD)
        await db.commit()

        # Markpoint service roles for the Target admin journey. `mission_manager`
        # and `point_admin` are granted to *different* accounts on purpose, so
        # the permission-separation journey has two distinct actors rather than
        # one account holding both.
        mission_manager = await role(db, "SERVICE", "mission_manager", "markpoint")
        point_admin = await role(db, "SERVICE", "point_admin", "markpoint")
        # Wagle roles are separate from Markpoint roles by design — a service
        # permission in one service confers nothing in the other. Both Family A
        # actors need `wagle.messages.*` explicitly or the Room returns 403.
        wagle_room_admin = await role(db, "SERVICE", "room_admin", "wagle")
        wagle_participant = await role(db, "SERVICE", "participant", "wagle")
        db.add_all((
            MembershipRoleAssignment(membership_id=memberships["owner_a"].id, role_id=mission_manager.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["admin"].id, role_id=point_admin.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["owner_a"].id, role_id=wagle_room_admin.id, assigned_by_account_id=accounts["owner_a"].id),
            MembershipRoleAssignment(membership_id=memberships["participant"].id, role_id=wagle_participant.id, assigned_by_account_id=accounts["owner_a"].id),
        ))
        await db.commit()

        # A Wagle room both Family A actors participate in — the two-browser
        # realtime journey needs a room with more than one participant.
        room = WagleRoom(
            family_group_id=alpha.id, room_type="GROUP", title="가족 대화",
            status="active", created_by_actor_type="ACCOUNT",
            created_by_account_id=accounts["owner_a"].id, next_message_sequence=0,
        )
        db.add(room)
        await db.flush()
        db.add_all((
            WagleParticipant(family_group_id=alpha.id, room_id=room.id, family_membership_id=memberships["owner_a"].id, room_role="room_admin", status="active", joined_sequence=0),
            WagleParticipant(family_group_id=alpha.id, room_id=room.id, family_membership_id=memberships["participant"].id, room_role="member", status="active", joined_sequence=0),
        ))

        # One mission per member state the Markpoint journeys need: one the
        # member can submit, and one already awaiting approval so the admin
        # journey has something to approve without depending on journey order.
        today = datetime.now(timezone.utc).date()
        db.add_all((
            MarkpointMission(
                family_group_id=alpha.id,
                assignee_membership_id=memberships["participant"].id,
                created_by_membership_id=memberships["owner_a"].id,
                scheduled_for=today, title="방 정리하기", reward_amount=30, status="active",
            ),
            MarkpointMission(
                family_group_id=alpha.id,
                assignee_membership_id=memberships["participant"].id,
                created_by_membership_id=memberships["owner_a"].id,
                scheduled_for=today, title="숙제 끝내기", reward_amount=20,
                status="pending_approval", submitted_at=now,
            ),
        ))
        await db.commit()
        print("PHASE1_SYNTHETIC_SEED_OK")
        print("WAVE6_TARGET_FIXTURE_OK")


if __name__ == "__main__":
    asyncio.run(main())
