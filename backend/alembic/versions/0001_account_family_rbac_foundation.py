"""Add Account, Family, membership, scoped Role, and Permission foundation."""
from alembic import op
import sqlalchemy as sa


revision = "0001_account_family_rbac"
down_revision = "0000_legacy_schema_baseline"
branch_labels = None
depends_on = None


def _timestamps() -> list:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    ]


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        *_timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active', 'suspended', 'deleted')", name="ck_accounts_status"),
    )
    op.create_table(
        "family_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        *_timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('active', 'suspended', 'closed')", name="ck_family_groups_status"),
    )
    op.create_table(
        "family_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("relationship", sa.String(length=30), nullable=False, server_default="unknown"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="invited"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("account_id", "family_group_id", name="uq_family_memberships_account_family"),
        sa.CheckConstraint("relationship IN ('mother', 'father', 'child', 'guardian', 'grandparent', 'other', 'unknown')", name="ck_family_memberships_relationship"),
        sa.CheckConstraint("status IN ('invited', 'active', 'suspended', 'left', 'removed')", name="ck_family_memberships_status"),
    )
    op.create_index("ix_family_memberships_account_family_status", "family_memberships", ["account_id", "family_group_id", "status"])
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scope_type", sa.String(length=20), nullable=False),
        sa.Column("service_code", sa.String(length=50), nullable=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *_timestamps(),
        sa.CheckConstraint("scope_type IN ('FAMILY', 'SERVICE')", name="ck_roles_scope_type"),
        sa.CheckConstraint("(scope_type = 'FAMILY' AND service_code IS NULL) OR (scope_type = 'SERVICE' AND service_code IS NOT NULL)", name="ck_roles_scope_service"),
    )
    op.create_index("uq_roles_scope_service_code", "roles", ["scope_type", sa.text("COALESCE(service_code, '')"), "code"], unique=True)
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="RESTRICT"), primary_key=True),
    )
    op.create_table(
        "membership_role_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("membership_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assigned_by_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("uq_active_membership_role", "membership_role_assignments", ["membership_id", "role_id"], unique=True, postgresql_where=sa.text("revoked_at IS NULL"))
    op.create_table(
        "service_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("service_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("family_group_id", "service_code", name="uq_service_subscriptions_family_service"),
        sa.CheckConstraint("status IN ('active', 'suspended', 'cancelled')", name="ck_service_subscriptions_status"),
    )
    op.create_table(
        "legacy_identity_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("legacy_system", sa.String(length=50), nullable=False),
        sa.Column("legacy_identity_type", sa.String(length=50), nullable=False),
        sa.Column("legacy_identity_id", sa.String(length=100), nullable=False),
        sa.Column("mapping_status", sa.String(length=20), nullable=False, server_default="candidate"),
        sa.Column("reviewed_by_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("legacy_system", "legacy_identity_type", "legacy_identity_id", name="uq_legacy_identity_source"),
        sa.CheckConstraint("mapping_status IN ('candidate', 'reviewed', 'linked', 'rejected', 'ambiguous')", name="ck_legacy_identity_mappings_status"),
    )
    op.execute("""
        INSERT INTO permissions (code, description) VALUES
          ('family.read', 'Read the active family context'),
          ('family.members.read', 'Read family memberships'),
          ('family.members.invite', 'Create a membership for an existing account'),
          ('family.members.manage', 'Update membership lifecycle or relationship'),
          ('family.roles.assign', 'Assign or revoke membership roles'),
          ('family.ownership.manage', 'Manage owner assignments and transfer'),
          ('family.services.manage', 'Manage family service subscriptions'),
          ('markpoint.own.read', 'Read own mapped MarkPoint data'),
          ('markpoint.missions.manage', 'Manage MarkPoint missions'),
          ('markpoint.points.adjust', 'Adjust MarkPoint points')
        ON CONFLICT (code) DO NOTHING
    """)
    op.execute("""
        INSERT INTO roles (scope_type, service_code, code, name, description) VALUES
          ('FAMILY', NULL, 'owner', 'Owner', 'Family owner with all initial family permissions'),
          ('FAMILY', NULL, 'admin', 'Admin', 'Delegated family administration'),
          ('FAMILY', NULL, 'member', 'Member', 'General family participant'),
          ('FAMILY', NULL, 'restricted_member', 'Restricted member', 'Limited family participant'),
          ('SERVICE', 'markpoint', 'participant', 'MarkPoint participant', 'Own MarkPoint access'),
          ('SERVICE', 'markpoint', 'mission_manager', 'Mission manager', 'MarkPoint mission management'),
          ('SERVICE', 'markpoint', 'point_admin', 'Point administrator', 'MarkPoint point adjustment')
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r CROSS JOIN permissions p
        WHERE r.scope_type = 'FAMILY' AND r.code = 'owner'
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON p.code IN
          ('family.read', 'family.members.read', 'family.members.invite',
           'family.members.manage', 'family.services.manage',
           'markpoint.missions.manage', 'markpoint.points.adjust')
        WHERE r.scope_type = 'FAMILY' AND r.code = 'admin'
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON p.code IN
          ('family.read', 'family.members.read', 'markpoint.own.read')
        WHERE r.scope_type = 'FAMILY' AND r.code = 'member'
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON p.code = 'markpoint.own.read'
        WHERE r.scope_type = 'FAMILY' AND r.code = 'restricted_member'
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON
          (r.code = 'participant' AND p.code = 'markpoint.own.read') OR
          (r.code = 'mission_manager' AND p.code = 'markpoint.missions.manage') OR
          (r.code = 'point_admin' AND p.code = 'markpoint.points.adjust')
        WHERE r.scope_type = 'SERVICE' AND r.service_code = 'markpoint'
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table("legacy_identity_mappings")
    op.drop_table("service_subscriptions")
    op.drop_index("uq_active_membership_role", table_name="membership_role_assignments")
    op.drop_table("membership_role_assignments")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_index("uq_roles_scope_service_code", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_family_memberships_account_family_status", table_name="family_memberships")
    op.drop_table("family_memberships")
    op.drop_table("family_groups")
    op.drop_table("accounts")
