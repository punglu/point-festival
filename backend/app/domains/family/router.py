"""Path-scoped Family Foundation APIs; legacy MarkPoint routes stay unchanged."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.domains.family import auth_service, service
from app.domains.family.dependencies import (
    get_current_account, get_current_session_id, require_family_permission,
)
from app.domains.family.models import Account, FamilyMembership, MembershipRoleAssignment, Role
from app.domains.family.schema import (
    AccountContextResponse, AccountLoginRequest, AccountLoginResponse,
    AuthorizedFamilySummary, FamilyCreate, FamilyResponse, FamilySummary,
    FamilyUpdate, MeResponse, MeUpdate, MemberAccountProvisionRequest,
    MemberAccountProvisionResponse, MembershipCreate, MembershipSelfUpdate, MembershipSummary,
    MembershipUpdate, PasswordChangeRequest, RefreshRequest, RefreshResponse,
    RoleAssignmentCreate, RoleAssignmentResponse, RoleSummary, SessionSummary,
    ServiceSubscriptionCreate, ServiceSubscriptionSummary, ServiceSubscriptionUpdate,
    SubscriptionResponse,
)


router = APIRouter(tags=["family-foundation"])


def _role_summary(role: Role) -> RoleSummary:
    return RoleSummary(code=role.code, scope_type=role.scope_type, service_code=role.service_code)


# --- Account-native auth (Wave 1, D2/D3) ---------------------------------
# These are Account-level, not family-scoped, so per D7 they do not sit under
# /families/{familyId}/. They never consult LegacyIdentityMapping.


@router.post("/api/auth/account/login", response_model=AccountLoginResponse)
async def account_login(req: AccountLoginRequest, db: AsyncSession = Depends(get_db)):
    """아이디 + 플랫폼 비밀번호 로그인 (D2). Issues an Account-scoped Session."""
    result = await auth_service.login(db, req.username, req.password, req.device_id, req.device_label)
    return AccountLoginResponse(**result)


@router.post("/api/auth/account/refresh", response_model=RefreshResponse)
async def account_refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Rotate the refresh token; the presented token is revoked in the same transaction."""
    result = await auth_service.refresh_session(db, req.refresh_token)
    return RefreshResponse(**result)


@router.post("/api/auth/account/logout", status_code=status.HTTP_204_NO_CONTENT)
async def account_logout(
    session_id: int = Depends(get_current_session_id),
    db: AsyncSession = Depends(get_db),
):
    """Revoke only the calling Session; other devices stay signed in."""
    await auth_service.logout(db, session_id)


@router.get("/api/me", response_model=MeResponse)
async def read_me(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Current Account plus its server-derived AuthorizedFamilySet (D1/D3)."""
    credential = await auth_service.get_credential_for_account(db, account.id)
    families = []
    for family, membership in await service.authorized_family_set(db, account.id):
        roles = await service.family_roles(db, membership.id)
        permissions = await service.effective_permissions(db, membership)
        families.append(
            AuthorizedFamilySummary(
                family_group_id=family.id,
                name=family.name,
                membership_id=membership.id,
                relationship=membership.relationship,
                joined_at=membership.joined_at,
                roles=[_role_summary(role) for role in roles],
                permissions=sorted(permissions),
            )
        )
    return MeResponse(
        account_id=account.id,
        display_name=account.display_name,
        is_password_change_required=bool(credential and credential.is_password_change_required),
        bio=account.bio,
        birthday=account.birthday,
        avatar_color=account.avatar_color,
        authorized_families=families,
    )


@router.patch("/api/me", response_model=MeResponse)
async def update_me(
    req: MeUpdate,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Self-service profile edit (W7.5 2z) -- own Account only, no permission
    beyond authentication (same self-service shape as `/api/me/password`)."""
    await service.update_account_profile(
        db, account,
        display_name=req.display_name, bio=req.bio, birthday=req.birthday, avatar_color=req.avatar_color,
    )
    return await read_me(account=account, db=db)


@router.patch("/api/families/{family_id}/members/me", response_model=MembershipSummary)
async def update_my_membership(
    family_id: int,
    data: MembershipSelfUpdate,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Self-service family-role label edit on one's own Membership (1f/2z).
    Deliberately bypasses `FAMILY_MEMBERS_MANAGE` -- a member declaring their
    own relationship is not the same authority as a FamilyAdmin managing
    someone else's, and `MembershipSelfUpdate` has no `status` field so this
    can never be used to activate/suspend/remove a Membership."""
    membership = await service.get_active_membership(db, account.id, family_id)
    membership = await service.update_own_membership_relationship(db, membership, data.relationship)
    return await _membership_summary(db, membership)


@router.post("/api/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    req: PasswordChangeRequest,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Change own password. Revokes every existing Session, including this one."""
    await auth_service.change_password(db, account.id, req.current_password, req.new_password)


@router.get("/api/me/sessions", response_model=list[SessionSummary])
async def list_my_sessions(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    rows = await auth_service.list_sessions(db, account.id)
    return [
        SessionSummary(
            id=row.id,
            device_id=row.device_id,
            device_label=row.device_label,
            issued_at=row.issued_at,
            expires_at=row.expires_at,
            last_seen_at=row.last_seen_at,
        )
        for row in rows
    ]


@router.delete("/api/me/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_my_device(
    device_id: str,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """Device unlink (D3): revokes every live Session for that device."""
    revoked = await auth_service.unlink_device(db, account.id, device_id)
    if revoked == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 기기의 활성 세션이 없습니다")


@router.post(
    "/api/families/{family_id}/member-accounts",
    response_model=MemberAccountProvisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def provision_member_account(
    family_id: int,
    req: MemberAccountProvisionRequest,
    authorized: tuple = Depends(require_family_permission(service.FAMILY_MEMBERS_PROVISION)),
    db: AsyncSession = Depends(get_db),
):
    """FamilyAdmin provisions an independent Account for a member of its own family.

    The path `family_id` is authorized by the dependency before this body runs,
    so a cross-family attempt is already rejected here.
    """
    actor_account, _actor_membership = authorized
    account, membership, initial_password = await service.provision_member_account(
        db,
        family_id,
        actor_account.id,
        req.display_name,
        req.username,
        req.relationship,
    )
    return MemberAccountProvisionResponse(
        account_id=account.id,
        membership_id=membership.id,
        username=auth_service.normalize_username(req.username),
        initial_password=initial_password,
        is_password_change_required=True,
    )


async def _membership_summary(db: AsyncSession, membership: FamilyMembership) -> MembershipSummary:
    account = await service.get_account(db, membership.account_id)
    return MembershipSummary(
        id=membership.id,
        account_id=membership.account_id,
        account_display_name=account.display_name if account else "",
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
