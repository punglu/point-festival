"""Add Doran Service Principal, Service-Room Binding, and service-event idempotency (R2-B1)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_doran_service_binding"
down_revision = "0002_doran_messaging_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)

    op.create_table(
        "service_principals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_code", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("credential_id", sa.String(64), nullable=False, unique=True),
        sa.Column("credential_hash", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('active', 'revoked')", name="ck_service_principals_status"),
    )

    op.create_table(
        "doran_service_bindings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_principal_id", sa.Integer(), sa.ForeignKey("service_principals.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("room_id", uuid, nullable=False),
        sa.Column("allowed_actions", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["room_id", "family_group_id"], ["doran_rooms.id", "doran_rooms.family_group_id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("service_principal_id", "room_id", name="uq_doran_service_binding_principal_room"),
        sa.CheckConstraint("status IN ('active', 'inactive')", name="ck_doran_service_bindings_status"),
    )
    op.create_index("ix_doran_service_bindings_principal", "doran_service_bindings", ["service_principal_id"])

    op.add_column("doran_messages", sa.Column("service_principal_id", sa.Integer(), sa.ForeignKey("service_principals.id", ondelete="RESTRICT"), nullable=True))
    op.add_column("doran_messages", sa.Column("source", sa.String(100), nullable=True))
    op.add_column("doran_messages", sa.Column("source_event_id", sa.String(128), nullable=True))
    op.create_check_constraint(
        "ck_doran_messages_service_actor",
        "doran_messages",
        "(message_type = 'SERVICE_ACTION' AND service_principal_id IS NOT NULL AND sender_participant_id IS NULL "
        "AND service_code IS NOT NULL AND source IS NOT NULL AND source_event_id IS NOT NULL) "
        "OR (message_type <> 'SERVICE_ACTION' AND service_principal_id IS NULL AND source IS NULL AND source_event_id IS NULL)",
    )
    op.create_index(
        "uq_doran_messages_service_idempotency",
        "doran_messages",
        ["service_principal_id", "source", "source_event_id"],
        unique=True,
        postgresql_where=sa.text("message_type = 'SERVICE_ACTION'"),
    )

    op.create_table(
        "doran_service_audit_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("service_principal_id", sa.Integer(), sa.ForeignKey("service_principals.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("family_group_id", sa.Integer(), nullable=True),
        sa.Column("room_id", uuid, nullable=True),
        sa.Column("result_code", sa.String(20), nullable=False),
        sa.Column("detail", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "event_type IN ('principal_created','principal_revoked','binding_created','binding_activated',"
            "'binding_deactivated','publish_success','replay_detected','permission_denied','schema_denied')",
            name="ck_doran_service_audit_event_type",
        ),
    )
    op.create_index("ix_doran_service_audit_log_principal_created", "doran_service_audit_log", ["service_principal_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_doran_service_audit_log_principal_created", table_name="doran_service_audit_log")
    op.drop_table("doran_service_audit_log")
    op.drop_index("uq_doran_messages_service_idempotency", table_name="doran_messages")
    op.drop_constraint("ck_doran_messages_service_actor", "doran_messages", type_="check")
    op.drop_column("doran_messages", "source_event_id")
    op.drop_column("doran_messages", "source")
    op.drop_column("doran_messages", "service_principal_id")
    op.drop_index("ix_doran_service_bindings_principal", table_name="doran_service_bindings")
    op.drop_table("doran_service_bindings")
    op.drop_table("service_principals")
