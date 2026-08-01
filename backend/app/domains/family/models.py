"""Target Foundation persistence models; legacy MarkPoint tables remain intact."""
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Account(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    display_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="active", server_default="active")
    __table_args__ = (CheckConstraint("status IN ('active', 'suspended', 'deleted')", name="ck_accounts_status"),)


class AccountCredential(Base, SoftDeleteMixin, TimestampMixin):
    """Account-native platform credential (D2).

    아이디 + 플랫폼 비밀번호. Email/phone are deliberately absent: D2 approves a
    username identifier and does not require either. The password is stored only
    as a bcrypt hash; no reversible form exists anywhere in this system.

    Not a Legacy bridge: this table never derives from, converts, or backfills
    `player_auth`/`admin_auth` rows (D8 RESET).
    """
    __tablename__ = "account_credentials"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    username = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="active", server_default="active")
    # An admin-issued first credential the member has not yet replaced.
    is_initial_credential = Column(Boolean, nullable=False, default=False, server_default="false")
    is_password_change_required = Column(Boolean, nullable=False, default=False, server_default="false")
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_attempt_count = Column(Integer, nullable=False, default=0, server_default="0")
    # Naming exception carried from the existing contract (see
    # MONGLE_DATA_NAMING_CONTRACT_V0_1 §3): a deadline, not an event timestamp.
    locked_until = Column(DateTime(timezone=True), nullable=True)
    # Issuer audit — which Account provisioned this credential (FamilyAdmin flow).
    issued_by_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        CheckConstraint("status IN ('active', 'disabled', 'revoked')", name="ck_account_credentials_status"),
        CheckConstraint("failed_attempt_count >= 0", name="ck_account_credentials_failed_attempt_count"),
    )


class AccountSession(Base, TimestampMixin):
    """Account-scoped persistent Session (D3).

    Scoped to the Account, never to one FamilyGroup: the whole
    `AuthorizedFamilySet` is derived per request from ACTIVE memberships, so
    ending one membership never invalidates the Session itself.

    Only the refresh token's SHA-256 hash is stored; the raw refresh token is
    returned to the caller once and is not recoverable from the database.
    `device_id` is a stable client-install identifier, which is what makes
    per-device listing and unlink possible without a separate Device aggregate.
    """
    __tablename__ = "account_sessions"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    refresh_token_hash = Column(String(64), nullable=False)
    device_id = Column(String(64), nullable=False)
    device_label = Column(String(100), nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(30), nullable=True)
    # Rotation chain: lets a replayed old refresh token be traced, not just denied.
    rotated_from_session_id = Column(Integer, ForeignKey("account_sessions.id", ondelete="SET NULL"), nullable=True)
    __table_args__ = (
        CheckConstraint(
            "revoked_reason IS NULL OR revoked_reason IN "
            "('logout', 'refresh_rotation', 'device_unlink', 'credential_reset', 'password_change', 'admin_revoke')",
            name="ck_account_sessions_revoked_reason",
        ),
    )


class FamilyGroup(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "family_groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="active", server_default="active")
    __table_args__ = (CheckConstraint("status IN ('active', 'suspended', 'closed')", name="ck_family_groups_status"),)


class FamilyMembership(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "family_memberships"
    id = Column(Integer, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    relationship = Column(String(30), nullable=False, default="unknown", server_default="unknown")
    status = Column(String(20), nullable=False, default="invited", server_default="invited")
    joined_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        UniqueConstraint("account_id", "family_group_id", name="uq_family_memberships_account_family"),
        UniqueConstraint("id", "family_group_id", name="uq_family_memberships_id_family"),
        CheckConstraint("relationship IN ('mother', 'father', 'child', 'guardian', 'grandparent', 'other', 'unknown')", name="ck_family_memberships_relationship"),
        CheckConstraint("status IN ('invited', 'active', 'suspended', 'left', 'removed')", name="ck_family_memberships_status"),
    )


class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    scope_type = Column(String(20), nullable=False)
    service_code = Column(String(50), nullable=True)
    code = Column(String(80), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, nullable=False, default=True, server_default="true")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    __table_args__ = (
        CheckConstraint("scope_type IN ('FAMILY', 'SERVICE')", name="ck_roles_scope_type"),
        CheckConstraint("(scope_type = 'FAMILY' AND service_code IS NULL) OR (scope_type = 'SERVICE' AND service_code IS NOT NULL)", name="ck_roles_scope_service"),
    )


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    code = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="RESTRICT"), primary_key=True)


class MembershipRoleAssignment(Base):
    __tablename__ = "membership_role_assignments"
    id = Column(Integer, primary_key=True)
    membership_id = Column(Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    assigned_by_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)


class ServiceSubscription(Base, TimestampMixin):
    __tablename__ = "service_subscriptions"
    id = Column(Integer, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    service_code = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="active", server_default="active")
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        UniqueConstraint("family_group_id", "service_code", name="uq_service_subscriptions_family_service"),
        CheckConstraint("status IN ('active', 'suspended', 'cancelled')", name="ck_service_subscriptions_status"),
    )


class LegacyIdentityMapping(Base):
    __tablename__ = "legacy_identity_mappings"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    legacy_system = Column(String(50), nullable=False)
    legacy_identity_type = Column(String(50), nullable=False)
    legacy_identity_id = Column(String(100), nullable=False)
    mapping_status = Column(String(20), nullable=False, default="candidate", server_default="candidate")
    reviewed_by_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("legacy_system", "legacy_identity_type", "legacy_identity_id", name="uq_legacy_identity_source"),
        CheckConstraint("mapping_status IN ('candidate', 'reviewed', 'linked', 'rejected', 'ambiguous')", name="ck_legacy_identity_mappings_status"),
    )
