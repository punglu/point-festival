from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FamilyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class FamilyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[str] = None


class MembershipCreate(BaseModel):
    account_id: int
    relationship: str = "unknown"
    status: str = "active"


class MembershipUpdate(BaseModel):
    relationship: Optional[str] = None
    status: Optional[str] = None


class RoleAssignmentCreate(BaseModel):
    role_code: str
    service_code: Optional[str] = None


class ServiceSubscriptionCreate(BaseModel):
    status: str = "active"


class ServiceSubscriptionUpdate(BaseModel):
    status: str


class RoleSummary(BaseModel):
    code: str
    scope_type: str
    service_code: Optional[str] = None


class MembershipSummary(BaseModel):
    id: int
    account_id: int
    family_group_id: int
    relationship: str
    status: str
    roles: List[RoleSummary] = []


class FamilySummary(BaseModel):
    id: int
    name: str
    status: str
    membership: MembershipSummary
    permissions: List[str] = []


class AccountContextResponse(BaseModel):
    account_id: int
    display_name: str
    families: List[FamilySummary]


class FamilyResponse(BaseModel):
    id: int
    name: str
    status: str


class RoleAssignmentResponse(BaseModel):
    id: int
    membership_id: int
    role: RoleSummary
    assigned_at: datetime


class SubscriptionResponse(BaseModel):
    id: int
    family_group_id: int
    service_code: str
    status: str
