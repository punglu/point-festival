"""W7.5 Phase D — SLICE-REWARD-CATALOG (1l/2h/2j, 보상 교환/리워드샵).

One catalog aggregate shared by three screens, per the Phase D Slice
Mapping. Redemption reuses the Ledger via a new self-service
`markpoint_target.service.self_spend` (not `adjust_points`, which needs an
admin-only permission code no child holds) rather than duplicating
point-debit logic.

Revision ID: 0018_reward_catalog
Revises: 0017_family_album
"""
from alembic import op
import sqlalchemy as sa

revision = "0018_reward_catalog"
down_revision = "0017_family_album"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reward_catalog_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("created_by_membership_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_reward_catalog_item_creator_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("cost >= 0", name="ck_reward_catalog_item_cost_nonnegative"),
    )
    op.create_index("ix_reward_catalog_items_family", "reward_catalog_items", ["family_group_id"])

    op.create_table(
        "reward_redemptions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("reward_item_id", sa.BigInteger(), sa.ForeignKey("reward_catalog_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("redeemed_by_membership_id", sa.Integer(), nullable=False),
        sa.Column("cost_at_redemption", sa.Integer(), nullable=False),
        sa.Column("ledger_entry_id", sa.BigInteger(), sa.ForeignKey("markpoint_ledger_entries.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["redeemed_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_reward_redemption_redeemer_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reward_redemptions_family", "reward_redemptions", ["family_group_id"])
    op.create_index("ix_reward_redemptions_member", "reward_redemptions", ["redeemed_by_membership_id"])


def downgrade() -> None:
    op.drop_index("ix_reward_redemptions_member", table_name="reward_redemptions")
    op.drop_index("ix_reward_redemptions_family", table_name="reward_redemptions")
    op.drop_table("reward_redemptions")
    op.drop_index("ix_reward_catalog_items_family", table_name="reward_catalog_items")
    op.drop_table("reward_catalog_items")
