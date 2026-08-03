"""W7.5 Phase D — SLICE-NOTIFICATION-LIST (1n, 알림 목록).

Account-native, deliberately **not** an extension of the legacy
`notification` domain: that table is `player_id`-scoped via
`LegacyIdentityMapping`, which D8 RESET explicitly excludes for new
Account-native users (no legacy identity import). This is a fresh table.

No producer route exists yet in this migration -- creating a notification
(e.g. on mission approval) is a future integration point, out of this
Slice's declared scope, which is the storage/read/mark-read contract the
`1n` screen itself needs.

Revision ID: 0019_account_notification
Revises: 0018_reward_catalog
"""
from alembic import op
import sqlalchemy as sa

revision = "0019_account_notification"
down_revision = "0018_reward_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_notifications",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=30), server_default="general", nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_account_notifications_account", "account_notifications", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_account_notifications_account", table_name="account_notifications")
    op.drop_table("account_notifications")
