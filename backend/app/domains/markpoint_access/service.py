"""Markpoint family-service access resolution (Wave 4, D5-A/D5-B).

Responsibility axis: access-status resolution, the activation lifecycle
(member request -> FamilyAdmin approval, plus FamilyAdmin direct activation),
and per-member access restriction for the Markpoint FAMILY service.

Deliberate boundaries:

- No `MarkpointParticipant` aggregate. Access is derived per request from
  `ServiceSubscription` + `FamilyMembership` minus any ACTIVE restriction,
  never stored as a separate membership-like row. A restriction is a
  subtraction from default access, and its absence is the normal state.
- Default access is not Mission participation. Nothing here creates, implies or
  requires a Mission record; that decision belongs entirely to Markpoint's own
  product routes (Wave 5).
- Activation does not grant ServiceAdmin, and neither does requesting it.
  `assign_service_admin`/`revoke_service_admin` are thin Markpoint-scoped
  wrappers over the existing `family.service.assign_role()`/
  `revoke_assignment()` writers -- gated by the same ACTIVE-`ServiceSubscription`
  check Wave 1 already built for every SERVICE-scope role -- not a separate
  grant path. They exist as their own routes (rather than reusing the generic
  `/members/{id}/roles` route) because that generic route is still
  legacy-token-gated (`get_current_user`, pre-dating Wave 1); Wave 4 is new
  Target-only work and authenticates the Account-native way throughout, per
  D2/D3.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.family import service as family_service
from app.domains.family.models import FamilyMembership, MembershipRoleAssignment, ServiceSubscription
from app.domains.markpoint_access.models import (
    MarkpointAccessRestriction, MarkpointActivationRequest,
)

SERVICE_CODE = "markpoint"
SERVICE_ADMIN_ROLE_CODES = ("mission_manager", "point_admin")


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _subscription(db: AsyncSession, family_id: int) -> Optional[ServiceSubscription]:
    stmt = select(ServiceSubscription).where(
        ServiceSubscription.family_group_id == family_id,
        ServiceSubscription.service_code == SERVICE_CODE,
    )
    return (await db.execute(stmt)).scalars().first()


async def active_restriction(
    db: AsyncSession, membership_id: int
) -> Optional[MarkpointAccessRestriction]:
    """The live restriction for one Membership, if any."""
    stmt = select(MarkpointAccessRestriction).where(
        MarkpointAccessRestriction.target_membership_id == membership_id,
        MarkpointAccessRestriction.service_code == SERVICE_CODE,
        MarkpointAccessRestriction.status == "ACTIVE",
    )
    return (await db.execute(stmt)).scalars().first()


async def get_access_status(db: AsyncSession, membership: FamilyMembership) -> dict:
    """Resolve one Account's Markpoint access for its own Membership.

    -- [Query] Access = ACTIVE ServiceSubscription AND ACTIVE Membership AND no
    -- ACTIVE restriction. Read-only; never creates a Mission-participation
    -- record -- Markpoint's own product routes (Wave 5) own that entirely, and
    -- having access is not the same as participating.
    """
    subscription = await _subscription(db, membership.family_group_id)
    subscription_status = subscription.status if subscription else "inactive"
    roles = await family_service.family_roles(db, membership.id)
    service_admin_roles = [
        role.code
        for role in roles
        if role.scope_type == "SERVICE" and role.service_code == SERVICE_CODE
    ]
    restriction = await active_restriction(db, membership.id)
    has_default_access = (
        subscription_status == "active"
        and membership.status == "active"
        and restriction is None
    )
    return {
        "family_group_id": membership.family_group_id,
        "service_code": SERVICE_CODE,
        "subscription_status": subscription_status,
        "membership_status": membership.status,
        "has_default_access": has_default_access,
        "is_restricted": restriction is not None,
        "restriction_reason": restriction.reason if restriction else None,
        "is_service_admin": bool(service_admin_roles),
        "service_admin_roles": service_admin_roles,
    }


# --- activation lifecycle -------------------------------------------------


async def _require_same_family_active_membership(
    db: AsyncSession, family_id: int, membership_id: int
) -> FamilyMembership:
    membership = await db.get(FamilyMembership, membership_id)
    if membership is None or membership.family_group_id != family_id or membership.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="가족 구성원을 찾을 수 없습니다")
    if membership.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="활성 가족 구성원이 아닙니다")
    return membership


async def request_activation(
    db: AsyncSession, family_id: int, requester: FamilyMembership
) -> MarkpointActivationRequest:
    """A FamilyMember asks its FamilyAdmin to activate Markpoint (D5-A3).

    -- [Intent] Record a pending activation request for this family.
    Requesting grants nothing on its own -- not access, not ownership, and not
    ServiceAdmin. The requester does not become an Owner on approval either.
    """
    subscription = await _subscription(db, family_id)
    if subscription is not None and subscription.status == "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 활성화된 서비스입니다")

    existing = (
        await db.execute(
            select(MarkpointActivationRequest).where(
                MarkpointActivationRequest.family_group_id == family_id,
                MarkpointActivationRequest.service_code == SERVICE_CODE,
                MarkpointActivationRequest.status == "PENDING",
            )
        )
    ).scalars().first()
    if existing is not None:
        # Idempotent for the same requester; a conflict for a different one, so
        # two members cannot silently overwrite each other's request.
        if existing.requester_membership_id == requester.id:
            return existing
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 대기 중인 활성화 요청이 있습니다")

    request = MarkpointActivationRequest(
        family_group_id=family_id,
        service_code=SERVICE_CODE,
        requester_membership_id=requester.id,
        status="PENDING",
    )
    db.add(request)
    try:
        await db.commit()
    except IntegrityError:
        # The partial unique index caught a concurrent request for this family.
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 대기 중인 활성화 요청이 있습니다")
    await db.refresh(request)
    return request


async def _load_pending_request(
    db: AsyncSession, family_id: int, request_id: int
) -> MarkpointActivationRequest:
    request = await db.get(MarkpointActivationRequest, request_id)
    if request is None or request.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="활성화 요청을 찾을 수 없습니다")
    if request.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 처리된 요청입니다")
    return request


async def approve_activation(
    db: AsyncSession,
    family_id: int,
    request_id: int,
    processor: FamilyMembership,
    note: Optional[str] = None,
) -> tuple[MarkpointActivationRequest, ServiceSubscription]:
    """FamilyAdmin approves a pending request and activates the service.

    -- [Intent] Mark the request APPROVED and bring the family-owned
    -- subscription to ACTIVE together. The requester gains no Owner or
    -- ServiceAdmin rights from this -- activation is not work authority.

    Both writes land in one transaction: the request mutations below are
    pending in this session when `set_subscription()` issues the single
    `commit()`, so an approved request can never be persisted without its
    subscription (or the reverse).
    """
    request = await _load_pending_request(db, family_id, request_id)
    request.status = "APPROVED"
    request.processed_by_membership_id = processor.id
    request.processed_at = _now()
    request.decision_note = note
    subscription = await family_service.set_subscription(db, family_id, SERVICE_CODE, "active")
    await db.refresh(request)
    return request, subscription


async def reject_activation(
    db: AsyncSession,
    family_id: int,
    request_id: int,
    processor: FamilyMembership,
    note: Optional[str] = None,
) -> MarkpointActivationRequest:
    """FamilyAdmin rejects a pending request. The service stays inactive."""
    request = await _load_pending_request(db, family_id, request_id)
    request.status = "REJECTED"
    request.processed_by_membership_id = processor.id
    request.processed_at = _now()
    request.decision_note = note
    await db.commit()
    await db.refresh(request)
    return request


async def list_activation_requests(
    db: AsyncSession, family_id: int
) -> list[MarkpointActivationRequest]:
    stmt = (
        select(MarkpointActivationRequest)
        .where(
            MarkpointActivationRequest.family_group_id == family_id,
            MarkpointActivationRequest.service_code == SERVICE_CODE,
        )
        .order_by(MarkpointActivationRequest.requested_at.desc())
    )
    return list((await db.execute(stmt)).scalars())


# --- individual restriction ----------------------------------------------


async def restrict_member(
    db: AsyncSession,
    family_id: int,
    target_membership_id: int,
    actor: FamilyMembership,
    reason: Optional[str] = None,
) -> MarkpointAccessRestriction:
    """Explicitly remove one member's default Markpoint access (D5-B).

    -- [Intent] Subtract default access for one Membership.
    -- [Audit] restricted_by_membership_id records the acting FamilyAdmin.
    Idempotent: restricting an already-restricted member returns the existing
    restriction rather than stacking rows.
    """
    target = await _require_same_family_active_membership(db, family_id, target_membership_id)
    existing = await active_restriction(db, target.id)
    if existing is not None:
        return existing

    restriction = MarkpointAccessRestriction(
        family_group_id=family_id,
        service_code=SERVICE_CODE,
        target_membership_id=target.id,
        status="ACTIVE",
        reason=reason,
        restricted_by_membership_id=actor.id,
    )
    db.add(restriction)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        existing = await active_restriction(db, target.id)
        if existing is None:
            raise
        return existing
    await db.refresh(restriction)
    return restriction


async def restore_member(
    db: AsyncSession, family_id: int, target_membership_id: int, actor: FamilyMembership
) -> MarkpointAccessRestriction:
    """Lift a restriction, returning the member to default access.

    The row is kept with `status='RESTORED'` rather than deleted, so the history
    of who restricted whom, and who lifted it, survives.
    """
    target = await _require_same_family_active_membership(db, family_id, target_membership_id)
    restriction = await active_restriction(db, target.id)
    if restriction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="활성 제한이 없습니다")
    restriction.status = "RESTORED"
    restriction.restored_by_membership_id = actor.id
    restriction.restored_at = _now()
    await db.commit()
    await db.refresh(restriction)
    return restriction


async def list_restrictions(
    db: AsyncSession, family_id: int
) -> list[MarkpointAccessRestriction]:
    stmt = (
        select(MarkpointAccessRestriction)
        .where(
            MarkpointAccessRestriction.family_group_id == family_id,
            MarkpointAccessRestriction.service_code == SERVICE_CODE,
        )
        .order_by(MarkpointAccessRestriction.restricted_at.desc())
    )
    return list((await db.execute(stmt)).scalars())


async def activate_directly(db: AsyncSession, family_id: int) -> ServiceSubscription:
    """FamilyAdmin direct activation (D5-A3 admin-direct path).

    Reuses the existing generic `ServiceSubscription` writer -- Markpoint's
    activation state is not a new physical concept, only this domain's own
    read/authorization surface over it. Idempotent: activating an
    already-ACTIVE subscription is a no-op re-affirmation, not an error, and
    grants no role to the activating Account.
    """
    return await family_service.set_subscription(db, family_id, SERVICE_CODE, "active")


async def assign_service_admin(
    db: AsyncSession, family_id: int, membership_id: int, role_code: str, actor_account_id: int
) -> MembershipRoleAssignment:
    """Explicit Markpoint ServiceAdmin grant (D4). Never automatic."""
    if role_code not in SERVICE_ADMIN_ROLE_CODES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="유효하지 않은 ServiceAdmin 역할입니다")
    membership = await db.get(FamilyMembership, membership_id)
    if membership is None or membership.family_group_id != family_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="가족 구성원을 찾을 수 없습니다")
    return await family_service.assign_role(db, family_id, membership, role_code, SERVICE_CODE, actor_account_id)


async def revoke_service_admin(db: AsyncSession, family_id: int, assignment_id: int) -> None:
    await family_service.revoke_assignment(db, family_id, assignment_id)
