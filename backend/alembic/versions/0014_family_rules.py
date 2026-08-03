"""W7.5 Phase D — SLICE-FAMILY-RULES (1v, 가족 규칙 설정).

Bounded, non-destructive, no policy blocker beyond ordinary product design
(Matrix note). One row per rule; `PUT` replaces the whole category list at
once, matching the Screen's own "edit the whole list" shape rather than
per-row CRUD (see the Phase D Slice Mapping doc).

Revision ID: 0014_family_rules
Revises: 0013_family_todo
"""
from alembic import op
import sqlalchemy as sa

revision = "0014_family_rules"
down_revision = "0013_family_todo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "family_rules",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("value_text", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_by_membership_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["updated_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_rule_actor_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("category IN ('life', 'point')", name="ck_family_rule_category"),
    )
    op.create_index("ix_family_rules_family", "family_rules", ["family_group_id"])


def downgrade() -> None:
    op.drop_index("ix_family_rules_family", table_name="family_rules")
    op.drop_table("family_rules")
