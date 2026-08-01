"""Add Account-native credential and persistent Session (D2/D3).

Wave 1. Creates the platform-owned login credential and Session stores that
`accounts` never had. Deliberately creates **no** data: under D8 RESET no
legacy `player_auth`/`admin_auth`/PIN row is read, converted, or backfilled by
this revision. Existing Foundation tables are untouched.
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_account_credential_session"
down_revision = "0004_doran_reliable_slice"
branch_labels = None
depends_on = None


def _timestamps() -> list:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    ]


def upgrade() -> None:
    op.create_table(
        "account_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("is_initial_credential", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_password_change_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issued_by_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active', 'disabled', 'revoked')", name="ck_account_credentials_status"),
        sa.CheckConstraint("failed_attempt_count >= 0", name="ck_account_credentials_failed_attempt_count"),
    )
    # Login identifier uniqueness. Partial on deleted_at so a soft-deleted row
    # never blocks reuse, while a merely disabled/revoked row still does — a
    # revoked username must not be re-registrable by someone else.
    op.create_index(
        "uq_account_credentials_username",
        "account_credentials",
        ["username"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    # One live credential per Account. Password reset updates this row in place
    # rather than accumulating rows.
    op.create_index(
        "uq_account_credentials_account",
        "account_credentials",
        ["account_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "account_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("device_label", sa.String(length=100), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(length=30), nullable=True),
        sa.Column(
            "rotated_from_session_id",
            sa.Integer(),
            sa.ForeignKey("account_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        *_timestamps(),
        sa.CheckConstraint(
            "revoked_reason IS NULL OR revoked_reason IN "
            "('logout', 'refresh_rotation', 'device_unlink', 'credential_reset', 'password_change', 'admin_revoke')",
            name="ck_account_sessions_revoked_reason",
        ),
    )
    # The refresh token hash is the lookup key for rotation and replay
    # detection, so it must be globally unique across live and revoked rows.
    op.create_index(
        "uq_account_sessions_refresh_token_hash",
        "account_sessions",
        ["refresh_token_hash"],
        unique=True,
    )
    # Device unlink revokes every session for one (account, device) pair.
    op.create_index(
        "ix_account_sessions_account_device",
        "account_sessions",
        ["account_id", "device_id"],
    )

    # Provisioning an independent Account + initial credential is a stronger
    # act than `family.members.invite` (which the 0001 seed defines as adding an
    # *existing* account), so it gets its own code rather than overloading that
    # one. Granted to the FamilyAdmin-class roles only: owner and admin.
    op.execute(
        """
        INSERT INTO permissions (code, description) VALUES
          ('family.members.provision', 'Provision an independent Account and initial credential for a family member')
        ON CONFLICT (code) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r JOIN permissions p ON p.code = 'family.members.provision'
        WHERE r.scope_type = 'FAMILY' AND r.code IN ('owner', 'admin')
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM role_permissions
        WHERE permission_id IN (SELECT id FROM permissions WHERE code = 'family.members.provision')
        """
    )
    op.execute("DELETE FROM permissions WHERE code = 'family.members.provision'")
    op.drop_index("ix_account_sessions_account_device", table_name="account_sessions")
    op.drop_index("uq_account_sessions_refresh_token_hash", table_name="account_sessions")
    op.drop_table("account_sessions")
    op.drop_index("uq_account_credentials_account", table_name="account_credentials")
    op.drop_index("uq_account_credentials_username", table_name="account_credentials")
    op.drop_table("account_credentials")
