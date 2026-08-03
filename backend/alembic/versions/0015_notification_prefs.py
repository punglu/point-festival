"""W7.5 Phase D — SLICE-NOTIFICATION-PREFERENCES (2n, 알림 세부설정).

Self-service, Account-native (not `family`-scoped -- a preference belongs
to the Account, not a Membership, same reasoning as `PATCH /api/me`).
One row per (account, key) rather than a JSON blob, so a future key can be
added without a data migration on existing rows -- a key with no row is
simply "not yet set", defaulted client-side.

Revision ID: 0015_notification_prefs
Revises: 0014_family_rules
"""
from alembic import op
import sqlalchemy as sa

revision = "0015_notification_prefs"
down_revision = "0014_family_rules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_notification_preferences",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("pref_key", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "pref_key", name="uq_account_notification_pref"),
    )
    op.create_index("ix_account_notification_prefs_account", "account_notification_preferences", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_account_notification_prefs_account", table_name="account_notification_preferences")
    op.drop_table("account_notification_preferences")
