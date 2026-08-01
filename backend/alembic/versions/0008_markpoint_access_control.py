"""Add Markpoint activation requests and per-member access restrictions.

Wave 4 (D5-A3 / D5-B). Two pieces of state the existing
`service_subscriptions` + RBAC tables cannot express:

- a member-initiated activation *request* awaiting FamilyAdmin approval, and
- an explicit per-member restriction that overrides default access.

Neither introduces a `MarkpointParticipant` aggregate. Default access stays
derived per request from `ServiceSubscription` + `FamilyMembership`; a
restriction row is a *subtraction* from that, not a membership record, and its
absence is the normal state.

Creates no operational data (D8 RESET).
"""
from alembic import op
import sqlalchemy as sa


# alembic_version.version_num is varchar(32) — keep this at or under 32 chars.
revision = "0008_markpoint_access_control"
down_revision = "0007_wagle_runtime_identifiers"
branch_labels = None
depends_on = None


def _timestamps() -> list:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    ]


def upgrade() -> None:
    op.create_table(
        "markpoint_activation_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("service_code", sa.String(length=50), nullable=False, server_default="markpoint"),
        sa.Column("requester_membership_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("processed_by_membership_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.String(length=300), nullable=True),
        *_timestamps(),
        sa.CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')",
            name="ck_markpoint_activation_requests_status",
        ),
        # A processed request must record who processed it and when; a pending
        # one must not pretend to have been. Keeps the audit trail honest at the
        # DB layer rather than relying on every caller.
        sa.CheckConstraint(
            "(status = 'PENDING' AND processed_at IS NULL AND processed_by_membership_id IS NULL) "
            "OR (status <> 'PENDING' AND processed_at IS NOT NULL)",
            name="ck_markpoint_activation_requests_processed",
        ),
    )
    # At most one open request per family+service. Partial, so a rejected or
    # approved request never blocks a later one — the row stays for audit.
    op.create_index(
        "uq_markpoint_activation_request_pending",
        "markpoint_activation_requests",
        ["family_group_id", "service_code"],
        unique=True,
        postgresql_where=sa.text("status = 'PENDING'"),
    )
    op.create_index(
        "ix_markpoint_activation_requests_family_status",
        "markpoint_activation_requests",
        ["family_group_id", "status"],
    )

    op.create_table(
        "markpoint_access_restrictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("service_code", sa.String(length=50), nullable=False, server_default="markpoint"),
        sa.Column("target_membership_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("reason", sa.String(length=300), nullable=True),
        sa.Column("restricted_by_membership_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("restricted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("restored_by_membership_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("restored_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.CheckConstraint("status IN ('ACTIVE', 'RESTORED')", name="ck_markpoint_access_restrictions_status"),
        sa.CheckConstraint(
            "(status = 'ACTIVE' AND restored_at IS NULL AND restored_by_membership_id IS NULL) "
            "OR (status = 'RESTORED' AND restored_at IS NOT NULL)",
            name="ck_markpoint_access_restrictions_restored",
        ),
        # The FK pair mirrors the existing wagle_participants pattern: a
        # restriction can only target a membership *of the same family*, enforced
        # by the composite FK rather than by application code alone.
        sa.ForeignKeyConstraint(
            ["target_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            ondelete="RESTRICT",
            name="fk_markpoint_restriction_target_family",
        ),
    )
    # One live restriction per member+service. Restoring sets status='RESTORED',
    # which releases the slot while keeping the history.
    op.create_index(
        "uq_markpoint_access_restriction_active",
        "markpoint_access_restrictions",
        ["target_membership_id", "service_code"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.create_index(
        "ix_markpoint_access_restrictions_family",
        "markpoint_access_restrictions",
        ["family_group_id", "service_code", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_markpoint_access_restrictions_family", table_name="markpoint_access_restrictions")
    op.drop_index("uq_markpoint_access_restriction_active", table_name="markpoint_access_restrictions")
    op.drop_table("markpoint_access_restrictions")
    op.drop_index("ix_markpoint_activation_requests_family_status", table_name="markpoint_activation_requests")
    op.drop_index("uq_markpoint_activation_request_pending", table_name="markpoint_activation_requests")
    op.drop_table("markpoint_activation_requests")
