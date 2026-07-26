"""Path-scoped Family Foundation APIs; legacy MarkPoint routes stay unchanged."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.domains.family import service
from app.domains.family.models import FamilyMembership, MembershipRoleAssignment, Role
from app.domains.family.schema import (
    AccountContextResponse, FamilyCreate, FamilyResponse, FamilySummary,
    FamilyUpdate, MembershipCreate, MembershipSummary, MembershipUpdate,
    RoleAssignmentCreate, RoleAssignmentResponse, RoleSummary,
    ServiceSubscriptionCreate, ServiceSubscriptionSummary, ServiceSubscriptionUpdate,
    SubscriptionResponse,
)


router = APIRouter(tags=["family-foundation"])


def _role_summary(role: Role) -> RoleSummary:
    return RoleSummary(code=role.code, scope_type=role.scope_type, service_code=role.service_code)


async def _membership_summary(db: AsyncSession, membership: FamilyMembership) -> MembershipSummary:
    return MembershipSummary(
        id=membership.id,
        account_id=membership.account_id,
        family_group_id=membership.family_group_id,
        relationship=membership.relationship,
        status=membership.status,
        roles=[_role_summary(role) for role in await service.family_roles(db, membership.id)],
    )


async def _family_summary(db: AsyncSession, family, membership: FamilyMembership) -> FamilySummary:
    return FamilySummary(
        id=family.id,
        name=family.name,
        status=family.status,
        membership=await _membership_summary(db, membership),
        permissions=sorted(await service.effective_permissions(db, membership)),
        services=[
            ServiceSubscriptionSummary(service_code=item.service_code, status=item.status)
            for item in await service.list_subscriptions(db, family.id)
        ],
    )


@router.get("/api/account-context", response_model=AccountContextResponse)
async def account_context(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = await service.resolve_current_account(db, user)
    families = []
    for membership in await service.active_memberships_for_account(db, account.id):
        family = await service.get_family(db, membership.family_group_id)
        families.append(await _family_summary(db, family, membership))
    return AccountContextResponse(account_id=account.id, display_name=account.display_name, families=families)


@router.post("/api/families", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(data: FamilyCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = await service.resolve_current_account(db, user)
    return await service.create_family(db, account, data.name)


@router.get("/api/families", response_model=list[FamilyResponse])
async def list_families(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = await service.resolve_current_account(db, user)
    result = []
    for membership in await service.active_memberships_for_account(db, account.id):
        result.append(await service.get_family(db, membership.family_group_id))
    return result


@router.get("/api/families/{family_id}", response_model=FamilyResponse)
async def get_family(family_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_READ)
    return await service.get_family(db, family_id)


@router.patch("/api/families/{family_id}", response_model=FamilyResponse)
async def update_family(family_id: int, data: FamilyUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    required_permission = (
        service.FAMILY_OWNERSHIP_MANAGE
        if data.status is not None
        else service.FAMILY_SERVICES_MANAGE
    )
    await service.require_permission(db, user, family_id, required_permission)
    family = await service.get_family(db, family_id)
    if data.name is not None:
        family.name = data.name
    if data.status is not None:
        family.status = data.status
    await db.commit()
    await db.refresh(family)
    return family


@router.get("/api/families/{family_id}/members", response_model=list[MembershipSummary])
async def list_members(family_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_MEMBERS_READ)
    memberships = list((await db.execute(select(FamilyMembership).where(FamilyMembership.family_group_id == family_id, FamilyMembership.deleted_at.is_(None)).order_by(FamilyMembership.id))).scalars())
    return [await _membership_summary(db, membership) for membership in memberships]


@router.post("/api/families/{family_id}/members", response_model=MembershipSummary, status_code=status.HTTP_201_CREATED)
async def create_membership(family_id: int, data: MembershipCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_MEMBERS_INVITE)
    await service.get_family(db, family_id)
    membership = await service.add_membership(db, family_id, data.account_id, data.relationship, data.status)
    return await _membership_summary(db, membership)


@router.patch("/api/families/{family_id}/members/{membership_id}", response_model=MembershipSummary)
async def update_membership(family_id: int, membership_id: int, data: MembershipUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_MEMBERS_MANAGE)
    membership = await db.get(FamilyMembership, membership_id)
    if membership is None or membership.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="가족 구성원을 찾을 수 없습니다")
    membership = await service.update_membership(db, membership, data.relationship, data.status)
    return await _membership_summary(db, membership)


@router.get("/api/families/{family_id}/members/{membership_id}/roles", response_model=list[RoleAssignmentResponse])
async def list_role_assignments(family_id: int, membership_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_MEMBERS_READ)
    stmt = select(MembershipRoleAssignment, Role).join(Role, Role.id == MembershipRoleAssignment.role_id).join(FamilyMembership, FamilyMembership.id == MembershipRoleAssignment.membership_id).where(FamilyMembership.family_group_id == family_id, MembershipRoleAssignment.membership_id == membership_id, MembershipRoleAssignment.revoked_at.is_(None))
    return [RoleAssignmentResponse(id=assignment.id, membership_id=assignment.membership_id, role=_role_summary(role), assigned_at=assignment.assigned_at) for assignment, role in (await db.execute(stmt)).all()]


@router.post("/api/families/{family_id}/members/{membership_id}/roles", response_model=RoleAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_role_assignment(family_id: int, membership_id: int, data: RoleAssignmentCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account, _ = await service.require_permission(db, user, family_id, service.FAMILY_ROLES_ASSIGN)
    membership = await db.get(FamilyMembership, membership_id)
    if membership is None or membership.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="가족 구성원을 찾을 수 없습니다")
    assignment = await service.assign_role(db, family_id, membership, data.role_code, data.service_code, account.id)
    role = await db.get(Role, assignment.role_id)
    return RoleAssignmentResponse(id=assignment.id, membership_id=assignment.membership_id, role=_role_summary(role), assigned_at=assignment.assigned_at)


@router.delete("/api/families/{family_id}/members/{membership_id}/roles/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_assignment(family_id: int, membership_id: int, assignment_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_ROLES_ASSIGN)
    assignment = await db.get(MembershipRoleAssignment, assignment_id)
    if assignment is None or assignment.membership_id != membership_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="역할 부여를 찾을 수 없습니다")
    await service.revoke_assignment(db, family_id, assignment_id)


@router.get("/api/families/{family_id}/services", response_model=list[SubscriptionResponse])
async def get_services(family_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_READ)
    return await service.list_subscriptions(db, family_id)


@router.post("/api/families/{family_id}/services/{service_code}", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_service(family_id: int, service_code: str, data: ServiceSubscriptionCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_SERVICES_MANAGE)
    return await service.set_subscription(db, family_id, service_code, data.status)


@router.patch("/api/families/{family_id}/services/{service_code}", response_model=SubscriptionResponse)
async def update_service(family_id: int, service_code: str, data: ServiceSubscriptionUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.require_permission(db, user, family_id, service.FAMILY_SERVICES_MANAGE)
    return await service.set_subscription(db, family_id, service_code, data.status)
