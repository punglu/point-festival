"""Rename the Wagle runtime identity from its historical `doran` name.

와글와글/Wagle is the Target product name; `doran` was the implementation name
it shipped under. This revision moves every **active runtime** identifier to
Wagle in one atomic step: tables, indexes, constraints, trigger functions,
permission codes, the service code, and any development Outbox rows.

Deliberately **not** a data migration. No operational row is created,
transformed or backfilled — the rows are the same rows, reached by a different
name. Under D8 RESET no legacy operational data is imported here or anywhere.

`doran` appears throughout this file as the **source value of the rename**,
which is the one place the historical name legitimately survives. After
`upgrade()` completes there is no active `doran` identifier left in the
database; after `downgrade()` there is no active `wagle` one.

Trigger functions are dropped and recreated rather than renamed: PostgreSQL
stores a plpgsql body as text and re-parses it at call time, so a function that
selects `FROM doran_rooms` keeps doing so after the table is renamed and would
fail at runtime. Renaming the function alone would have left exactly that
latent break.
"""
from alembic import op


# alembic_version.version_num is varchar(32) — keep this at or under 32 chars.
revision = "0007_wagle_runtime_identifiers"
down_revision = "0006_family_service_separation"
branch_labels = None
depends_on = None


TABLES = [
    "doran_rooms",
    "doran_direct_pairs",
    "doran_participants",
    "doran_messages",
    "doran_participant_read_states",
    "doran_service_bindings",
    "doran_service_audit_log",
]

# Standalone indexes (partial-unique and plain). Constraint-backed indexes are
# renamed implicitly by ALTER TABLE ... RENAME CONSTRAINT and are not listed.
INDEXES = [
    "uq_doran_active_direct_pair",
    "uq_doran_active_participant",
    "ix_doran_participants_room_status",
    "ix_doran_messages_room_sequence",
    "uq_doran_messages_service_idempotency",
    "ix_doran_service_audit_log_principal_created",
    "ix_doran_service_bindings_principal",
]

# (table_after_rename, constraint_name). Every primary key, unique, check and
# foreign key whose name carries the historical prefix.
CONSTRAINTS = [
    ("wagle_rooms", "doran_rooms_pkey"),
    ("wagle_rooms", "uq_doran_rooms_id_family"),
    ("wagle_rooms", "ck_doran_rooms_type"),
    ("wagle_rooms", "ck_doran_rooms_status"),
    ("wagle_rooms", "ck_doran_rooms_actor"),
    ("wagle_rooms", "doran_rooms_family_group_id_fkey"),
    ("wagle_rooms", "doran_rooms_created_by_account_id_fkey"),
    ("wagle_direct_pairs", "doran_direct_pairs_pkey"),
    ("wagle_direct_pairs", "ck_doran_direct_pair_order"),
    ("wagle_direct_pairs", "doran_direct_pairs_room_id_fkey"),
    ("wagle_direct_pairs", "doran_direct_pairs_family_group_id_fkey"),
    ("wagle_direct_pairs", "doran_direct_pairs_membership_low_id_fkey"),
    ("wagle_direct_pairs", "doran_direct_pairs_membership_high_id_fkey"),
    ("wagle_direct_pairs", "doran_direct_pairs_membership_low_id_family_group_id_fkey"),
    ("wagle_direct_pairs", "doran_direct_pairs_membership_high_id_family_group_id_fkey"),
    ("wagle_participants", "doran_participants_pkey"),
    ("wagle_participants", "ck_doran_participants_role"),
    ("wagle_participants", "ck_doran_participants_status"),
    ("wagle_participants", "ck_doran_participants_sequence_range"),
    ("wagle_participants", "doran_participants_room_id_family_group_id_fkey"),
    ("wagle_participants", "doran_participants_family_membership_id_family_group_id_fkey"),
    ("wagle_messages", "doran_messages_pkey"),
    ("wagle_messages", "uq_doran_messages_room_sequence"),
    ("wagle_messages", "uq_doran_messages_sender_client"),
    ("wagle_messages", "ck_doran_messages_type"),
    ("wagle_messages", "ck_doran_messages_text_body"),
    ("wagle_messages", "ck_doran_messages_service_actor"),
    ("wagle_messages", "doran_messages_room_id_family_group_id_fkey"),
    ("wagle_messages", "doran_messages_sender_participant_id_fkey"),
    ("wagle_messages", "doran_messages_service_principal_id_fkey"),
    ("wagle_messages", "doran_messages_deleted_by_account_id_fkey"),
    ("wagle_participant_read_states", "doran_participant_read_states_pkey"),
    ("wagle_participant_read_states", "ck_doran_read_state_nonnegative"),
    ("wagle_participant_read_states", "doran_participant_read_states_participant_id_fkey"),
    ("wagle_service_bindings", "doran_service_bindings_pkey"),
    ("wagle_service_bindings", "ck_doran_service_bindings_status"),
    ("wagle_service_bindings", "uq_doran_service_binding_principal_room"),
    ("wagle_service_bindings", "uq_doran_service_binding_principal_family"),
    ("wagle_service_bindings", "doran_service_bindings_service_principal_id_fkey"),
    ("wagle_service_bindings", "doran_service_bindings_family_group_id_fkey"),
    ("wagle_service_bindings", "doran_service_bindings_room_id_family_group_id_fkey"),
    ("wagle_service_audit_log", "doran_service_audit_log_pkey"),
    ("wagle_service_audit_log", "ck_doran_service_audit_event_type"),
    ("wagle_service_audit_log", "doran_service_audit_log_service_principal_id_fkey"),
]

PERMISSIONS = [
    ("doran.messages.read", "wagle.messages.read"),
    ("doran.messages.send", "wagle.messages.send"),
    ("doran.rooms.create", "wagle.rooms.create"),
    ("doran.rooms.manage", "wagle.rooms.manage"),
    ("doran.participants.manage", "wagle.participants.manage"),
]


def _swap(name: str, frm: str, to: str) -> str:
    return name.replace(frm, to, 1)


# Guard object names use a bare `doran`/`wagle` prefix and are NOT derived from
# the table names — the real objects are `fn_<prefix>_service_binding_room_guard`
# (singular "binding") while the table is `<prefix>_service_bindings` (plural).
# Deriving one from the other silently mismatched on the first attempt: the
# `DROP ... IF EXISTS` matched nothing, the old objects survived, and the
# database briefly held both a doran and a wagle guard where the doran pair
# referenced tables that no longer existed.
def _binding_guard_sql(prefix: str, rooms: str, bindings: str) -> str:
    return f"""
        CREATE OR REPLACE FUNCTION fn_{prefix}_service_binding_room_guard() RETURNS trigger AS $$
        DECLARE
            room_type_val TEXT;
            room_family_val INTEGER;
        BEGIN
            SELECT room_type, family_group_id INTO room_type_val, room_family_val
            FROM {rooms} WHERE id = NEW.room_id;
            IF room_type_val IS NULL THEN
                RAISE EXCEPTION '{bindings}.room_id % does not reference an existing Room', NEW.room_id;
            END IF;
            IF room_type_val <> 'SERVICE' THEN
                RAISE EXCEPTION '{bindings}.room_id % must reference a SERVICE Room (found %)', NEW.room_id, room_type_val;
            END IF;
            IF room_family_val <> NEW.family_group_id THEN
                RAISE EXCEPTION '{bindings}.family_group_id % does not match bound Room family %', NEW.family_group_id, room_family_val;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """


def _room_guard_sql(prefix: str, rooms: str, bindings: str) -> str:
    return f"""
        CREATE OR REPLACE FUNCTION fn_{prefix}_room_binding_integrity_guard() RETURNS trigger AS $$
        BEGIN
            IF (NEW.room_type <> OLD.room_type OR NEW.family_group_id <> OLD.family_group_id) THEN
                IF EXISTS (SELECT 1 FROM {bindings} WHERE room_id = OLD.id) THEN
                    RAISE EXCEPTION 'Room % has an active Service Binding; room_type/family_group_id cannot change', OLD.id;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """


def _drop_guards(name_prefix: str, rooms: str, bindings: str) -> None:
    """Drop both backstops.

    `name_prefix` is the prefix the *objects* currently carry; `rooms`/`bindings`
    are the tables they currently sit on. The two differ during a rename, which
    is why they are separate parameters.
    """
    op.execute(f"DROP TRIGGER IF EXISTS trg_{name_prefix}_service_binding_room_guard ON {bindings}")
    op.execute(f"DROP TRIGGER IF EXISTS trg_{name_prefix}_room_binding_integrity_guard ON {rooms}")
    op.execute(f"DROP FUNCTION IF EXISTS fn_{name_prefix}_service_binding_room_guard()")
    op.execute(f"DROP FUNCTION IF EXISTS fn_{name_prefix}_room_binding_integrity_guard()")


def _create_guards(name_prefix: str, rooms: str, bindings: str) -> None:
    """Recreate both backstops against the given table names."""
    op.execute(_binding_guard_sql(name_prefix, rooms, bindings))
    op.execute(_room_guard_sql(name_prefix, rooms, bindings))
    op.execute(
        f"CREATE TRIGGER trg_{name_prefix}_service_binding_room_guard "
        f"BEFORE INSERT OR UPDATE ON {bindings} "
        f"FOR EACH ROW EXECUTE FUNCTION fn_{name_prefix}_service_binding_room_guard()"
    )
    op.execute(
        f"CREATE TRIGGER trg_{name_prefix}_room_binding_integrity_guard "
        f"BEFORE UPDATE ON {rooms} "
        f"FOR EACH ROW EXECUTE FUNCTION fn_{name_prefix}_room_binding_integrity_guard()"
    )


def upgrade() -> None:
    # Guards go first: their plpgsql bodies name the tables textually, so they
    # must not be left pointing at names that are about to disappear.
    _drop_guards(name_prefix="doran", rooms="doran_rooms", bindings="doran_service_bindings")
    # Tables next, so constraint/index renames address the new names.
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} RENAME TO {_swap(table, 'doran', 'wagle')}")
    for table, constraint in CONSTRAINTS:
        op.execute(
            f"ALTER TABLE {table} RENAME CONSTRAINT {constraint} TO {_swap(constraint, 'doran', 'wagle')}"
        )
    for index in INDEXES:
        op.execute(f"ALTER INDEX {index} RENAME TO {_swap(index, 'doran', 'wagle')}")

    _create_guards(name_prefix="wagle", rooms="wagle_rooms", bindings="wagle_service_bindings")

    # Permission codes. role_permissions references permissions.id, so updating
    # the code in place preserves every existing role binding.
    for old_code, new_code in PERMISSIONS:
        op.execute(f"UPDATE permissions SET code = '{new_code}' WHERE code = '{old_code}'")
    # Service code, on both the role registry and any family's subscription.
    op.execute("UPDATE roles SET service_code = 'wagle' WHERE service_code = 'doran'")
    op.execute("UPDATE service_subscriptions SET service_code = 'wagle' WHERE service_code = 'doran'")
    op.execute("UPDATE service_principals SET service_code = 'wagle' WHERE service_code = 'doran'")
    # Development Outbox rows written before the naming correction. Operational
    # data does not exist yet (D8 RESET), so this only tidies dev/test state.
    op.execute(
        "UPDATE service_outbox_events SET owner_service = 'wagle' WHERE owner_service = 'doran'"
    )
    op.execute(
        "UPDATE service_outbox_events SET event_type = 'wagle.message.created' "
        "WHERE event_type = 'doran.message.created'"
    )
    op.execute(
        "UPDATE service_outbox_events SET aggregate_type = 'wagle_message' "
        "WHERE aggregate_type = 'doran_message'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE service_outbox_events SET aggregate_type = 'doran_message' "
        "WHERE aggregate_type = 'wagle_message'"
    )
    op.execute(
        "UPDATE service_outbox_events SET event_type = 'doran.message.created' "
        "WHERE event_type = 'wagle.message.created'"
    )
    op.execute(
        "UPDATE service_outbox_events SET owner_service = 'doran' WHERE owner_service = 'wagle'"
    )
    op.execute("UPDATE service_principals SET service_code = 'doran' WHERE service_code = 'wagle'")
    op.execute("UPDATE service_subscriptions SET service_code = 'doran' WHERE service_code = 'wagle'")
    op.execute("UPDATE roles SET service_code = 'doran' WHERE service_code = 'wagle'")
    for old_code, new_code in PERMISSIONS:
        op.execute(f"UPDATE permissions SET code = '{old_code}' WHERE code = '{new_code}'")

    _drop_guards(name_prefix="wagle", rooms="wagle_rooms", bindings="wagle_service_bindings")
    for index in INDEXES:
        op.execute(f"ALTER INDEX {_swap(index, 'doran', 'wagle')} RENAME TO {index}")
    for table, constraint in CONSTRAINTS:
        op.execute(
            f"ALTER TABLE {table} RENAME CONSTRAINT {_swap(constraint, 'doran', 'wagle')} TO {constraint}"
        )
    for table in TABLES:
        op.execute(f"ALTER TABLE {_swap(table, 'doran', 'wagle')} RENAME TO {table}")

    _create_guards(name_prefix="doran", rooms="doran_rooms", bindings="doran_service_bindings")
