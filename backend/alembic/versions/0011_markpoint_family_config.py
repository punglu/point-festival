"""Wave 5 Core: per-Family Markpoint cycle configuration (MP-S04).

Revision ID kept short: `alembic_version.version_num` is `varchar(32)`, and a
36-character id in Wave 1 silently rolled back while the log still printed
"Running upgrade".

**No legacy backfill (D8 RESET).** The legacy installation-wide `configs` row
holding `point_cycle` is not copied into any Family here. Doing so would look
helpful and would be wrong twice over: it would assert that every Family had
agreed to the old global cycle, and it would make one Family's later change
appear to originate from data it never set. Families start unconfigured and
fall back to the documented default until an admin sets one explicitly.

Revision ID: 0011_markpoint_family_config
Revises: 0010_markpoint_target_ledger
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_markpoint_family_config"
down_revision = "0010_markpoint_target_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "markpoint_family_configs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("cycle_type", sa.String(length=20), server_default="weekly", nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("updated_by_membership_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        # Same-family enforcement for the actor, at the database rather than in
        # the service: an admin of another Family must not be recordable as the
        # one who changed this Family's cycle, even by a buggy caller.
        sa.ForeignKeyConstraint(
            ["updated_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_markpoint_family_config_actor_family",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        # Singular per Family — every guard depends on "the current cycle"
        # having exactly one answer.
        sa.UniqueConstraint("family_group_id", name="uq_markpoint_family_config_family"),
        # The value set is the legacy one, unchanged. `get_cycle_range` can
        # only compute periods for these six; a seventh would be a cycle with
        # no computable boundary.
        sa.CheckConstraint(
            "cycle_type IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')",
            name="ck_markpoint_family_config_cycle",
        ),
        sa.CheckConstraint("effective_to >= effective_from", name="ck_markpoint_family_config_range"),
    )
    op.create_index(
        "ix_markpoint_family_configs_family",
        "markpoint_family_configs",
        ["family_group_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_markpoint_family_configs_family", table_name="markpoint_family_configs")
    op.drop_table("markpoint_family_configs")
