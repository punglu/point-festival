from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ServiceAdminAssignRequest(BaseModel):
    membership_id: int
    role_code: str = Field(..., description="mission_manager or point_admin")


class ServiceAdminAssignmentResponse(BaseModel):
    id: int
    membership_id: int
    role_code: str
    assigned_at: datetime


class MarkpointAccessResponse(BaseModel):
    family_group_id: int
    service_code: str
    subscription_status: str
    membership_status: str
    has_default_access: bool
    is_restricted: bool = False
    restriction_reason: str | None = None
    is_service_admin: bool
    service_admin_roles: List[str] = []


class ActivationRequestCreate(BaseModel):
    """No fields: the requester is the authenticated Membership, and the
    service is Markpoint by route. Accepting a requester id here would let a
    caller request on someone else's behalf."""


class ActivationDecisionRequest(BaseModel):
    decision_note: str | None = Field(default=None, max_length=300)


class ActivationRequestResponse(BaseModel):
    id: int
    family_group_id: int
    service_code: str
    requester_membership_id: int
    status: str
    processed_by_membership_id: int | None = None
    requested_at: datetime
    processed_at: datetime | None = None
    decision_note: str | None = None

    model_config = {"from_attributes": True}


class RestrictionCreateRequest(BaseModel):
    target_membership_id: int
    reason: str | None = Field(default=None, max_length=300)


class RestrictionResponse(BaseModel):
    id: int
    family_group_id: int
    service_code: str
    target_membership_id: int
    status: str
    reason: str | None = None
    restricted_by_membership_id: int
    restricted_at: datetime
    restored_by_membership_id: int | None = None
    restored_at: datetime | None = None

    model_config = {"from_attributes": True}


class MarkpointActivationResponse(BaseModel):
    family_group_id: int
    service_code: str
    status: str
