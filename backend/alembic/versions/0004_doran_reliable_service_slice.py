"""Add generic Transactional Outbox and a PostgreSQL cross-table backstop for
Doran Service Bindings (R2-B2)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_doran_reliable_slice"
down_revision = "0003_doran_service_binding"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_outbox_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("owner_service", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("event_version", sa.Integer(), nullable=False),
        sa.Column("aggregate_type", sa.String(50), nullable=False),
        sa.Column("aggregate_id", sa.String(64), nullable=False),
        sa.Column("source_event_id", sa.String(128), nullable=False),
        sa.Column("family_id", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("owner_service", "source_event_id", name="uq_service_outbox_owner_source_event"),
        sa.CheckConstraint("status IN ('PENDING', 'PROCESSING', 'PUBLISHED', 'DEAD')", name="ck_service_outbox_status"),
    )
    op.create_index("ix_service_outbox_claim", "service_outbox_events", ["status", "next_attempt_at"])
    op.create_index("ix_service_outbox_owner_type", "service_outbox_events", ["owner_service", "event_type"])

    # Canonical-Room invariant: at most one Binding per (Principal, Family),
    # required for the Worker's idempotent get-or-create of the canonical
    # SERVICE Room per Family.
    op.create_unique_constraint(
        "uq_doran_service_binding_principal_family",
        "doran_service_bindings",
        ["service_principal_id", "family_group_id"],
    )

    # Cross-table backstop (a plain CHECK cannot reference another table): a
    # Binding's room_id must point at a SERVICE Room in the same Family. The
    # composite FK already guarantees the Family match; this trigger adds the
    # room_type guarantee and re-validates both on every write.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_doran_service_binding_room_guard() RETURNS TRIGGER AS $$
        DECLARE
            room_type_val TEXT;
            room_family_val INTEGER;
        BEGIN
            SELECT room_type, family_group_id INTO room_type_val, room_family_val
            FROM doran_rooms WHERE id = NEW.room_id;
            IF room_type_val IS NULL THEN
                RAISE EXCEPTION 'doran_service_bindings.room_id % does not reference an existing Room', NEW.room_id;
            END IF;
            IF room_type_val <> 'SERVICE' THEN
                RAISE EXCEPTION 'doran_service_bindings.room_id % must reference a SERVICE Room (found %)', NEW.room_id, room_type_val;
            END IF;
            IF room_family_val <> NEW.family_group_id THEN
                RAISE EXCEPTION 'doran_service_bindings.family_group_id % does not match bound Room family %', NEW.family_group_id, room_family_val;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_doran_service_binding_room_guard
        BEFORE INSERT OR UPDATE ON doran_service_bindings
        FOR EACH ROW EXECUTE FUNCTION fn_doran_service_binding_room_guard();
        """
    )

    # The reverse direction: a Room that already has a Binding must not be
    # mutated into a non-SERVICE type or reassigned to a different Family
    # out from under that Binding.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_doran_room_binding_integrity_guard() RETURNS TRIGGER AS $$
        BEGIN
            IF (NEW.room_type <> OLD.room_type OR NEW.family_group_id <> OLD.family_group_id) THEN
                IF EXISTS (SELECT 1 FROM doran_service_bindings WHERE room_id = OLD.id) THEN
                    RAISE EXCEPTION 'Room % has an active Service Binding; room_type/family_group_id cannot change', OLD.id;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_doran_room_binding_integrity_guard
        BEFORE UPDATE ON doran_rooms
        FOR EACH ROW EXECUTE FUNCTION fn_doran_room_binding_integrity_guard();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_doran_room_binding_integrity_guard ON doran_rooms")
    op.execute("DROP FUNCTION IF EXISTS fn_doran_room_binding_integrity_guard()")
    op.execute("DROP TRIGGER IF EXISTS trg_doran_service_binding_room_guard ON doran_service_bindings")
    op.execute("DROP FUNCTION IF EXISTS fn_doran_service_binding_room_guard()")
    op.drop_constraint("uq_doran_service_binding_principal_family", "doran_service_bindings", type_="unique")
    op.drop_index("ix_service_outbox_owner_type", table_name="service_outbox_events")
    op.drop_index("ix_service_outbox_claim", table_name="service_outbox_events")
    op.drop_table("service_outbox_events")
