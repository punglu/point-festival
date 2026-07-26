"""Server-side Account, Membership, Role, and Permission evaluation."""
from datetime import datetime, timezone
from typing import Iterable, Optional, Set

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.family.models import (
    Account, FamilyGroup, FamilyMembership, LegacyIdentityMapping,
    MembershipRoleAssignment, Permission, Role, RolePermission,
    ServiceSubscription,
)
from app.domains.auth.models import AdminAuth, PlayerAuth
from app.domains.player.models import Player


FAMILY_READ = "family.read"
FAMILY_MEMBERS_READ = "family.members.read"
FAMILY_MEMBERS_INVITE = "family.members.invite"
FAMILY_MEMBERS_MANAGE = "family.members.manage"
FAMILY_ROLES_ASSIGN = "family.roles.assign"
FAMILY_OWNERSHIP_MANAGE = "family.ownership.manage"
FAMILY_SERVICES_MANAGE = "family.services.manage"


def _legacy_identity(user: dict) -> tuple[str, str, str]:
    # The legacy dependency exposes player_id/is_admin.  Keep the Foundation
    # adapter compatible while never trusting a client supplied Account id.
    if "player_id" in user:
        return "markpoint", "player_auth", str(user["player_id"])
    if user.get("role") == "admin":
        return "markpoint", "admin_auth", str(user["sub"])
    return "markpoint", "player_auth", str(user["sub"])


async def resolve_current_account(db: AsyncSession, user: dict) -> Account:
    legacy_system, identity_type, identity_id = _legacy_identity(user)
    try:
        legacy_id = int(identity_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 레거시 인증입니다")

    if identity_type == "player_auth":
        legacy_identity = (
            await db.execute(
                select(PlayerAuth.id)
                .join(Player, Player.id == PlayerAuth.player_id)
                .where(
                    PlayerAuth.player_id == legacy_id,
                    PlayerAuth.deleted_at.is_(None),
                    Player.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
    else:
        legacy_identity = (
            await db.execute(
                select(AdminAuth.id)
                .outerjoin(Player, Player.id == AdminAuth.player_id)
                .where(
                    AdminAuth.id == legacy_id,
                    AdminAuth.deleted_at.is_(None),
                    (AdminAuth.player_id.is_(None) | Player.deleted_at.is_(None)),
                )
            )
        ).scalar_one_or_none()
    if legacy_identity is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="활성 레거시 인증이 필요합니다")

    stmt = (
        select(Account)
        .join(LegacyIdentityMapping, LegacyIdentityMapping.account_id == Account.id)
        .where(
            LegacyIdentityMapping.legacy_system == legacy_system,
            LegacyIdentityMapping.legacy_identity_type == identity_type,
            LegacyIdentityMapping.legacy_identity_id == identity_id,
            LegacyIdentityMapping.mapping_status == "linked",
            Account.status == "active",
            Account.deleted_at.is_(None),
        )
    )
    account = (await db.execute(stmt)).scalars().first()
    if account is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="계정 매핑이 필요합니다")
    return account


async def get_active_membership(db: AsyncSession, account_id: int, family_id: int) -> FamilyMembership:
    stmt = (
        select(FamilyMembership)
        .join(FamilyGroup, FamilyGroup.id == FamilyMembership.family_group_id)
        .where(
            FamilyMembership.account_id == account_id,
            FamilyMembership.family_group_id == family_id,
            FamilyMembership.status == "active",
            FamilyMembership.deleted_at.is_(None),
            FamilyGroup.status == "active",
            FamilyGroup.deleted_at.is_(None),
        )
    )
    membership = (await db.execute(stmt)).scalars().first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="활성 가족 구성원 권한이 필요합니다")
    return membership


async def effective_permissions(db: AsyncSession, membership: FamilyMembership) -> Set[str]:
    family = await db.get(FamilyGroup, membership.family_group_id)
    if family is None or family.status != "active" or family.deleted_at is not None:
        return set()
    stmt = (
        select(Permission.code, Role.scope_type, Role.service_code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(MembershipRoleAssignment, MembershipRoleAssignment.role_id == Role.id)
        .where(
            MembershipRoleAssignment.membership_id == membership.id,
            MembershipRoleAssignment.revoked_at.is_(None),
            Role.is_active.is_(True),
        )
    )
    permissions: Set[str] = set()
    for code, scope_type, service_code in (await db.execute(stmt)).all():
        if scope_type == "FAMILY":
            permissions.add(code)
            continue
        subscription = (
            await db.execute(
                select(ServiceSubscription.id).where(
                    ServiceSubscription.family_group_id == membership.family_group_id,
                    ServiceSubscription.service_code == service_code,
                    ServiceSubscription.status == "active",
                )
            )
        ).scalar_one_or_none()
        if subscription is not None:
            permissions.add(code)
    return permissions


async def require_permission(db: AsyncSession, user: dict, family_id: int, permission: str) -> tuple[Account, FamilyMembership]:
    account = await resolve_current_account(db, user)
    membership = await get_active_membership(db, account.id, family_id)
    if permission not in await effective_permissions(db, membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다")
    return account, membership


async def family_roles(db: AsyncSession, membership_id: int) -> list[Role]:
    stmt = (
        select(Role)
        .join(MembershipRoleAssignment, MembershipRoleAssignment.role_id == Role.id)
        .where(MembershipRoleAssignment.membership_id == membership_id, MembershipRoleAssignment.revoked_at.is_(None))
        .order_by(Role.scope_type, Role.code)
    )
    return list((await db.execute(stmt)).scalars())


async def create_family(db: AsyncSession, account: Account, name: str) -> FamilyGroup:
    owner = (
        await db.execute(select(Role).where(Role.scope_type == "FAMILY", Role.code == "owner", Role.is_active.is_(True)))
    ).scalars().first()
    if owner is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="권한 registry가 초기화되지 않았습니다")
    family = FamilyGroup(name=name, status="active")
    db.add(family)
    await db.flush()
    membership = FamilyMembership(
        family_group_id=family.id,
        account_id=account.id,
        relationship="unknown",
        status="active",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.flush()
    db.add(MembershipRoleAssignment(membership_id=membership.id, role_id=owner.id, assigned_by_account_id=account.id))
    await db.commit()
    await db.refresh(family)
    return family


async def get_family(db: AsyncSession, family_id: int) -> FamilyGroup:
    family = await db.get(FamilyGroup, family_id)
    if family is None or family.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="가족을 찾을 수 없습니다")
    return family


async def active_memberships_for_account(db: AsyncSession, account_id: int) -> list[FamilyMembership]:
    stmt = (
        select(FamilyMembership)
        .join(FamilyGroup, FamilyGroup.id == FamilyMembership.family_group_id)
        .where(
            FamilyMembership.account_id == account_id,
            FamilyMembership.status == "active",
            FamilyMembership.deleted_at.is_(None),
            FamilyGroup.status == "active",
            FamilyGroup.deleted_at.is_(None),
        )
    )
    return list((await db.execute(stmt)).scalars())


async def add_membership(db: AsyncSession, family_id: int, account_id: int, relationship: str, membership_status: str) -> FamilyMembership:
    account = await db.get(Account, account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="활성 계정이 필요합니다")
    membership = FamilyMembership(
        family_group_id=family_id,
        account_id=account_id,
        relationship=relationship,
        status=membership_status,
        joined_at=datetime.now(timezone.utc) if membership_status == "active" else None,
    )
    db.add(membership)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 가족 구성원입니다")
    await db.refresh(membership)
    return membership


async def _active_owner_count(db: AsyncSession, family_id: int) -> int:
    stmt = (
        select(MembershipRoleAssignment.id)
        .join(FamilyMembership, FamilyMembership.id == MembershipRoleAssignment.membership_id)
        .join(Role, Role.id == MembershipRoleAssignment.role_id)
        .where(
            FamilyMembership.family_group_id == family_id,
            FamilyMembership.status == "active",
            FamilyMembership.deleted_at.is_(None),
            MembershipRoleAssignment.revoked_at.is_(None),
            Role.scope_type == "FAMILY",
            Role.code == "owner",
        )
    )
    return len((await db.execute(stmt)).all())


async def _lock_family_for_owner_change(db: AsyncSession, family_id: int) -> None:
    """Serialize owner removal/suspension decisions for a single Family."""
    family = (
        await db.execute(select(FamilyGroup).where(FamilyGroup.id == family_id).with_for_update())
    ).scalars().first()
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="가족을 찾을 수 없습니다")


async def update_membership(db: AsyncSession, membership: FamilyMembership, relationship: Optional[str], membership_status: Optional[str]) -> FamilyMembership:
    if membership_status in {"suspended", "left", "removed"}:
        roles = await family_roles(db, membership.id)
        if any(role.scope_type == "FAMILY" and role.code == "owner" for role in roles):
            await _lock_family_for_owner_change(db, membership.family_group_id)
            if await _active_owner_count(db, membership.family_group_id) <= 1:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="마지막 Owner는 비활성화할 수 없습니다")
    if relationship is not None:
        membership.relationship = relationship
    if membership_status is not None:
        membership.status = membership_status
    await db.commit()
    await db.refresh(membership)
    return membership


async def assign_role(db: AsyncSession, family_id: int, membership: FamilyMembership, role_code: str, service_code: Optional[str], actor_account_id: int) -> MembershipRoleAssignment:
    stmt = select(Role).where(Role.code == role_code, Role.is_active.is_(True))
    if service_code is None:
        stmt = stmt.where(Role.scope_type == "FAMILY", Role.service_code.is_(None))
    else:
        stmt = stmt.where(Role.scope_type == "SERVICE", Role.service_code == service_code)
    role = (await db.execute(stmt)).scalars().first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할을 찾을 수 없습니다")
    if role.scope_type == "SERVICE":
        active = (
            await db.execute(select(ServiceSubscription.id).where(ServiceSubscription.family_group_id == family_id, ServiceSubscription.service_code == role.service_code, ServiceSubscription.status == "active"))
        ).scalar_one_or_none()
        if active is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="활성 서비스 구독이 필요합니다")
    existing = (
        await db.execute(select(MembershipRoleAssignment).where(MembershipRoleAssignment.membership_id == membership.id, MembershipRoleAssignment.role_id == role.id, MembershipRoleAssignment.revoked_at.is_(None)))
    ).scalars().first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 부여된 역할입니다")
    assignment = MembershipRoleAssignment(membership_id=membership.id, role_id=role.id, assigned_by_account_id=actor_account_id)
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def revoke_assignment(db: AsyncSession, family_id: int, assignment_id: int) -> None:
    assignment = await db.get(MembershipRoleAssignment, assignment_id)
    if assignment is None or assignment.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할 부여를 찾을 수 없습니다")
    membership = await db.get(FamilyMembership, assignment.membership_id)
    role = await db.get(Role, assignment.role_id)
    if membership is None or role is None or membership.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할 부여를 찾을 수 없습니다")
    if role.scope_type == "FAMILY" and role.code == "owner" and membership.status == "active":
        await _lock_family_for_owner_change(db, family_id)
        if await _active_owner_count(db, family_id) <= 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="마지막 Owner 역할은 제거할 수 없습니다")
    assignment.revoked_at = datetime.now(timezone.utc)
    await db.commit()


async def list_subscriptions(db: AsyncSession, family_id: int) -> list[ServiceSubscription]:
    return list((await db.execute(select(ServiceSubscription).where(ServiceSubscription.family_group_id == family_id).order_by(ServiceSubscription.service_code))).scalars())


async def set_subscription(db: AsyncSession, family_id: int, service_code: str, subscription_status: str) -> ServiceSubscription:
    subscription = (
        await db.execute(select(ServiceSubscription).where(ServiceSubscription.family_group_id == family_id, ServiceSubscription.service_code == service_code))
    ).scalars().first()
    now = datetime.now(timezone.utc)
    if subscription is None:
        subscription = ServiceSubscription(family_group_id=family_id, service_code=service_code, status=subscription_status, started_at=now if subscription_status == "active" else None)
        db.add(subscription)
    else:
        subscription.status = subscription_status
        subscription.started_at = now if subscription_status == "active" else subscription.started_at
        subscription.ended_at = now if subscription_status != "active" else None
    await db.commit()
    await db.refresh(subscription)
    return subscription
