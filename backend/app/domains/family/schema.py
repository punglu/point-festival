from datetime import date, datetime
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


# --- Account-native auth (Wave 1, D2/D3) ---------------------------------


class AccountLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1, max_length=200)
    # Stable per-install identifier so sessions can be listed and unlinked per
    # device. Supplied by the client; it is not a security boundary on its own.
    device_id: str = Field(..., min_length=1, max_length=64)
    device_label: Optional[str] = Field(default=None, max_length=100)


class AccountLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    account_id: int
    display_name: str
    is_password_change_required: bool


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    account_id: int


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=200)
    new_password: str = Field(..., min_length=1, max_length=200)


class SessionSummary(BaseModel):
    id: int
    device_id: str
    device_label: Optional[str] = None
    issued_at: datetime
    expires_at: datetime
    last_seen_at: Optional[datetime] = None


class AuthorizedFamilySummary(BaseModel):
    """One entry of the server-derived AuthorizedFamilySet."""
    family_group_id: int
    name: str
    membership_id: int
    relationship: str
    joined_at: Optional[datetime] = None
    roles: List[RoleSummary] = []
    permissions: List[str] = []


class MeResponse(BaseModel):
    account_id: int
    display_name: str
    is_password_change_required: bool
    bio: Optional[str] = None
    birthday: Optional[date] = None
    avatar_color: Optional[str] = None
    authorized_families: List[AuthorizedFamilySummary] = []


class MeUpdate(BaseModel):
    """Self-service profile edit (W7.5 2z). `display_name` is intentionally
    editable here too -- it is the same field auth/family summaries read,
    kept singular rather than duplicated behind a second write path."""
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=200)
    birthday: Optional[date] = None
    avatar_color: Optional[str] = Field(default=None, min_length=4, max_length=7, pattern=r"^#[0-9A-Fa-f]{3,6}$")


class MembershipSelfUpdate(BaseModel):
    """Self-service relationship label edit on one's own Membership only
    (1f/2z's family-role field). Deliberately excludes `status` -- that stays
    FamilyAdmin-only via the existing MembershipUpdate/require_permission path."""
    relationship: str = Field(..., pattern="^(mother|father|child|guardian|grandparent|other|unknown)$")


class MemberAccountProvisionRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=150)
    relationship: str = "unknown"


class MemberAccountProvisionResponse(BaseModel):
    account_id: int
    membership_id: int
    username: str
    # Returned exactly once, at creation. Never retrievable again.
    initial_password: str
    is_password_change_required: bool


class MembershipSummary(BaseModel):
    id: int
    account_id: int
    account_display_name: str
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
    services: List['ServiceSubscriptionSummary'] = []


class AccountContextResponse(BaseModel):
    account_id: int
    display_name: str
    families: List[FamilySummary]
    # DEFECT-001 (MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-
    # REMEDIATION-001): whether this Account is linked (via the existing
    # LegacyIdentityMapping bridge) to a real legacy admin_auth identity --
    # not a new authority, the same "one identity, two credential systems"
    # bridge /api/account-context already resolves through. Additive field;
    # every existing consumer that ignores it is unaffected.
    is_admin: bool = False


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


class ServiceSubscriptionSummary(BaseModel):
    service_code: str
    status: str
