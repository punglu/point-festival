"""Wave 3: Wagle Push subscriptions, per-endpoint delivery attempts, device PIN.

Revision ID kept short on purpose: `alembic_version.version_num` is
``varchar(32)``, and a 36-character id in Wave 1 caused the migration to roll
back while the log still printed "Running upgrade" — the failure was only
visible by querying `alembic_version` afterwards.

Adds no message, sequence or cursor table. Realtime resume reads Wave 2's
existing `wagle_messages.sequence`; a second cursor store could disagree with
the read state it shadows.

D8 RESET: nothing here backfills. No legacy PIN is copied into
`wagle_device_pins`, and no legacy notification row becomes a Push
subscription — these tables start empty by contract, not by omission.

Revision ID: 0009_wagle_realtime_push_pin
Revises: 0008_markpoint_access_control
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_wagle_realtime_push_pin"
down_revision = "0008_markpoint_access_control"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wagle_push_subscriptions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh_key", sa.String(length=255), nullable=False),
        sa.Column("auth_secret", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=60), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('active', 'expired', 'revoked')",
            name="ck_wagle_push_subscriptions_status",
        ),
    )
    # Partial unique indexes rather than plain ones: a device that re-registers
    # or an endpoint that is re-issued must replace its live row, while the
    # historical revoked/expired rows stay for audit. A full unique index would
    # force us to delete that history.
    op.create_index(
        "uq_wagle_push_subscription_active_endpoint",
        "wagle_push_subscriptions",
        ["endpoint"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "uq_wagle_push_subscription_active_device",
        "wagle_push_subscriptions",
        ["account_id", "device_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "ix_wagle_push_subscriptions_account_status",
        "wagle_push_subscriptions",
        ["account_id", "status"],
    )

    op.create_table(
        "wagle_push_delivery_attempts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("outbox_event_id", sa.BigInteger(), nullable=False),
        sa.Column("subscription_id", sa.BigInteger(), nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_error_code", sa.String(length=60), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["outbox_event_id"], ["service_outbox_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["wagle_push_subscriptions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        # Delivery idempotency lives here, in the database. At-least-once means
        # the same Outbox row WILL be processed again; without this constraint
        # that is a duplicate notification on the user's phone.
        sa.UniqueConstraint(
            "outbox_event_id", "subscription_id", name="uq_wagle_push_attempt_event_subscription"
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'SENT', 'FAILED', 'EXPIRED_ENDPOINT')",
            name="ck_wagle_push_attempt_status",
        ),
    )
    op.create_index(
        "ix_wagle_push_attempts_family_status",
        "wagle_push_delivery_attempts",
        ["family_group_id", "status"],
    )

    op.create_table(
        "wagle_device_pins",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=128), nullable=False),
        sa.Column("pin_hash", sa.String(length=255), nullable=False),
        sa.Column("pin_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("failed_attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_unlocked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        # Device isolation is this constraint: each device carries its own row
        # and its own attempt counter, so brute-forcing one device cannot lock
        # the Account out of another.
        sa.UniqueConstraint("account_id", "device_id", name="uq_wagle_device_pin_account_device"),
        sa.CheckConstraint("failed_attempt_count >= 0", name="ck_wagle_device_pin_attempts"),
    )
    op.create_index("ix_wagle_device_pins_account", "wagle_device_pins", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_wagle_device_pins_account", table_name="wagle_device_pins")
    op.drop_table("wagle_device_pins")

    op.drop_index("ix_wagle_push_attempts_family_status", table_name="wagle_push_delivery_attempts")
    op.drop_table("wagle_push_delivery_attempts")

    op.drop_index(
        "ix_wagle_push_subscriptions_account_status", table_name="wagle_push_subscriptions"
    )
    op.drop_index(
        "uq_wagle_push_subscription_active_device", table_name="wagle_push_subscriptions"
    )
    op.drop_index(
        "uq_wagle_push_subscription_active_endpoint", table_name="wagle_push_subscriptions"
    )
    op.drop_table("wagle_push_subscriptions")
