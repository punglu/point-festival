"""Markpoint family-service access routes (Wave 4, D5-A/D5-B/D7).

Family-scoped under `/api/families/{family_id}/markpoint/*` per D7. Every
route resolves the Account-native Session and revalidates ACTIVE Membership
in the path family via `family.dependencies` -- the Wave 1 Target boundary --
never the legacy player/admin path, since this is new Target-only work.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.family import service as family_service
from app.domains.family.dependencies import (
    get_family_membership, require_family_permission,
)
from app.domains.family.models import FamilyMembership
from app.domains.markpoint_access import service
from app.domains.markpoint_access.schema import (
    ActivationDecisionRequest, ActivationRequestResponse,
    MarkpointAccessResponse, MarkpointActivationResponse,
    RestrictionCreateRequest, RestrictionResponse,
    ServiceAdminAssignRequest, ServiceAdminAssignmentResponse,
)

router = APIRouter(tags=["markpoint-access"])


@router.get("/api/families/{family_id}/markpoint/access", response_model=MarkpointAccessResponse)
async def get_markpoint_access(
    membership: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    """The calling Account's own Markpoint access in this family.

    Read-only; computes default access from ServiceSubscription + Membership
    state on every call rather than trusting a cached or client-sent value.
    """
    return MarkpointAccessResponse(**await service.get_access_status(db, membership))


@router.post(
    "/api/families/{family_id}/markpoint/activate",
    response_model=MarkpointActivationResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_markpoint(
    family_id: int,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """FamilyAdmin direct activation (D5-A3). Idempotent; grants no role."""
    subscription = await service.activate_directly(db, family_id)
    return MarkpointActivationResponse(
        family_group_id=subscription.family_group_id,
        service_code=subscription.service_code,
        status=subscription.status,
    )


@router.post(
    "/api/families/{family_id}/markpoint/activation-requests",
    response_model=ActivationRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_markpoint_activation(
    family_id: int,
    membership: FamilyMembership = Depends(get_family_membership),
    db: AsyncSession = Depends(get_db),
):
    """A FamilyMember requests activation (D5-A3 member-request path).

    Any ACTIVE member of the path family may ask; no extra permission is
    required because asking grants nothing. The requester is the authenticated
    Membership, never a value from the request body.
    """
    return ActivationRequestResponse.model_validate(
        await service.request_activation(db, family_id, membership)
    )


@router.get(
    "/api/families/{family_id}/markpoint/activation-requests",
    response_model=list[ActivationRequestResponse],
)
async def list_markpoint_activation_requests(
    family_id: int,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """FamilyAdmin reviews this family's activation requests."""
    return [
        ActivationRequestResponse.model_validate(row)
        for row in await service.list_activation_requests(db, family_id)
    ]


@router.post(
    "/api/families/{family_id}/markpoint/activation-requests/{request_id}/approve",
    response_model=ActivationRequestResponse,
)
async def approve_markpoint_activation(
    family_id: int,
    request_id: int,
    req: ActivationDecisionRequest,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """FamilyAdmin approves and activates. Grants the requester no admin role."""
    _actor_account, actor_membership = authorized
    request, _subscription = await service.approve_activation(
        db, family_id, request_id, actor_membership, req.decision_note
    )
    return ActivationRequestResponse.model_validate(request)


@router.post(
    "/api/families/{family_id}/markpoint/activation-requests/{request_id}/reject",
    response_model=ActivationRequestResponse,
)
async def reject_markpoint_activation(
    family_id: int,
    request_id: int,
    req: ActivationDecisionRequest,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """FamilyAdmin rejects. The service stays inactive."""
    _actor_account, actor_membership = authorized
    return ActivationRequestResponse.model_validate(
        await service.reject_activation(db, family_id, request_id, actor_membership, req.decision_note)
    )


@router.post(
    "/api/families/{family_id}/markpoint/restrictions",
    response_model=RestrictionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def restrict_markpoint_member(
    family_id: int,
    req: RestrictionCreateRequest,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Explicitly remove one member's default access (D5-B). Idempotent."""
    _actor_account, actor_membership = authorized
    return RestrictionResponse.model_validate(
        await service.restrict_member(db, family_id, req.target_membership_id, actor_membership, req.reason)
    )


@router.delete(
    "/api/families/{family_id}/markpoint/restrictions/{target_membership_id}",
    response_model=RestrictionResponse,
)
async def restore_markpoint_member(
    family_id: int,
    target_membership_id: int,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Lift a restriction, returning the member to default access."""
    _actor_account, actor_membership = authorized
    return RestrictionResponse.model_validate(
        await service.restore_member(db, family_id, target_membership_id, actor_membership)
    )


@router.get(
    "/api/families/{family_id}/markpoint/restrictions",
    response_model=list[RestrictionResponse],
)
async def list_markpoint_restrictions(
    family_id: int,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    return [
        RestrictionResponse.model_validate(row)
        for row in await service.list_restrictions(db, family_id)
    ]


@router.post(
    "/api/families/{family_id}/markpoint/service-admins",
    response_model=ServiceAdminAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_markpoint_service_admin(
    family_id: int,
    req: ServiceAdminAssignRequest,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Explicit Markpoint ServiceAdmin grant (D4). FamilyAdmin only; never automatic."""
    actor_account, _actor_membership = authorized
    assignment = await service.assign_service_admin(
        db, family_id, req.membership_id, req.role_code, actor_account.id
    )
    return ServiceAdminAssignmentResponse(
        id=assignment.id,
        membership_id=assignment.membership_id,
        role_code=req.role_code,
        assigned_at=assignment.assigned_at,
    )


@router.delete(
    "/api/families/{family_id}/markpoint/service-admins/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_markpoint_service_admin(
    family_id: int,
    assignment_id: int,
    authorized: tuple = Depends(require_family_permission(family_service.FAMILY_SERVICES_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Explicit Markpoint ServiceAdmin revocation (D4). FamilyAdmin only."""
    await service.revoke_service_admin(db, family_id, assignment_id)
