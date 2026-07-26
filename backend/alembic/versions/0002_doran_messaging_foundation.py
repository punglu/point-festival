"""Add secure Family-scoped Doran messaging foundation."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_doran_messaging_foundation"
down_revision = "0001_account_family_rbac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_unique_constraint("uq_family_memberships_id_family", "family_memberships", ["id", "family_group_id"])
    op.create_table("doran_rooms",
        sa.Column("id", uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("room_type", sa.String(20), nullable=False), sa.Column("title", sa.String(200)),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_by_actor_type", sa.String(20), nullable=False),
        sa.Column("created_by_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT")),
        sa.Column("next_message_sequence", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("closed_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("id", "family_group_id", name="uq_doran_rooms_id_family"),
        sa.CheckConstraint("room_type IN ('DIRECT', 'GROUP', 'SERVICE')", name="ck_doran_rooms_type"), sa.CheckConstraint("status IN ('active', 'read_only', 'closed', 'deleted')", name="ck_doran_rooms_status"), sa.CheckConstraint("created_by_actor_type IN ('ACCOUNT', 'SERVICE', 'SYSTEM')", name="ck_doran_rooms_actor"))
    op.create_table("doran_direct_pairs",
        sa.Column("room_id", uuid, sa.ForeignKey("doran_rooms.id", ondelete="RESTRICT"), primary_key=True), sa.Column("family_group_id", sa.Integer(), sa.ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False), sa.Column("membership_low_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False), sa.Column("membership_high_id", sa.Integer(), sa.ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.ForeignKeyConstraint(["membership_low_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["membership_high_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], ondelete="RESTRICT"), sa.CheckConstraint("membership_low_id < membership_high_id", name="ck_doran_direct_pair_order"))
    op.create_index("uq_doran_active_direct_pair", "doran_direct_pairs", ["family_group_id", "membership_low_id", "membership_high_id"], unique=True, postgresql_where=sa.text("is_active"))
    op.create_table("doran_participants",
        sa.Column("id", uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")), sa.Column("family_group_id", sa.Integer(), nullable=False), sa.Column("room_id", uuid, nullable=False), sa.Column("family_membership_id", sa.Integer(), nullable=False), sa.Column("room_role", sa.String(20), nullable=False, server_default="member"), sa.Column("status", sa.String(20), nullable=False, server_default="active"), sa.Column("joined_sequence", sa.BigInteger(), nullable=False), sa.Column("left_sequence", sa.BigInteger()), sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("left_at", sa.DateTime(timezone=True)), sa.Column("removed_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["room_id", "family_group_id"], ["doran_rooms.id", "doran_rooms.family_group_id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["family_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], ondelete="RESTRICT"), sa.CheckConstraint("room_role IN ('room_admin', 'member')", name="ck_doran_participants_role"), sa.CheckConstraint("status IN ('active', 'left', 'removed')", name="ck_doran_participants_status"), sa.CheckConstraint("left_sequence IS NULL OR left_sequence >= joined_sequence", name="ck_doran_participants_sequence_range"))
    op.create_index("uq_doran_active_participant", "doran_participants", ["room_id", "family_membership_id"], unique=True, postgresql_where=sa.text("status = 'active'")); op.create_index("ix_doran_participants_room_status", "doran_participants", ["room_id", "status"])
    op.create_table("doran_messages",
        sa.Column("id", uuid, primary_key=True, server_default=sa.text("gen_random_uuid()")), sa.Column("family_group_id", sa.Integer(), nullable=False), sa.Column("room_id", uuid, nullable=False), sa.Column("sequence", sa.BigInteger(), nullable=False), sa.Column("sender_participant_id", uuid, sa.ForeignKey("doran_participants.id", ondelete="RESTRICT")), sa.Column("message_type", sa.String(20), nullable=False, server_default="TEXT"), sa.Column("client_message_id", sa.String(64)), sa.Column("body", sa.Text()), sa.Column("reply_to_message_id", uuid), sa.Column("service_code", sa.String(50)), sa.Column("service_payload_version", sa.Integer()), sa.Column("service_payload", postgresql.JSONB()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("deleted_at", sa.DateTime(timezone=True)), sa.Column("deleted_by_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="RESTRICT")), sa.ForeignKeyConstraint(["room_id", "family_group_id"], ["doran_rooms.id", "doran_rooms.family_group_id"], ondelete="RESTRICT"), sa.UniqueConstraint("room_id", "sequence", name="uq_doran_messages_room_sequence"), sa.UniqueConstraint("sender_participant_id", "room_id", "client_message_id", name="uq_doran_messages_sender_client"), sa.CheckConstraint("message_type IN ('TEXT', 'SYSTEM', 'SERVICE_ACTION')", name="ck_doran_messages_type"), sa.CheckConstraint("(message_type = 'TEXT' AND body IS NOT NULL AND length(body) BETWEEN 1 AND 4000) OR message_type <> 'TEXT'", name="ck_doran_messages_text_body"))
    op.create_index("ix_doran_messages_room_sequence", "doran_messages", ["room_id", "sequence"])
    op.create_table("doran_participant_read_states", sa.Column("participant_id", uuid, sa.ForeignKey("doran_participants.id", ondelete="RESTRICT"), primary_key=True), sa.Column("last_read_sequence", sa.BigInteger(), nullable=False, server_default="0"), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.CheckConstraint("last_read_sequence >= 0", name="ck_doran_read_state_nonnegative"))
    op.execute("""INSERT INTO permissions(code, description) VALUES ('doran.rooms.create','Create Doran rooms'),('doran.rooms.manage','Manage own Doran rooms'),('doran.participants.manage','Manage Doran participants'),('doran.messages.read','Read Doran messages'),('doran.messages.send','Send Doran messages') ON CONFLICT (code) DO NOTHING""")
    op.execute("""INSERT INTO roles(scope_type, service_code, code, name, description) VALUES ('SERVICE','doran','participant','Doran participant','Read and send in assigned Rooms'),('SERVICE','doran','room_admin','Doran room admin','Manage assigned Rooms') ON CONFLICT DO NOTHING""")
    op.execute("""INSERT INTO role_permissions(role_id, permission_id) SELECT r.id,p.id FROM roles r JOIN permissions p ON p.code IN ('doran.messages.read','doran.messages.send') WHERE r.scope_type='SERVICE' AND r.service_code='doran' AND r.code IN ('participant','room_admin') ON CONFLICT DO NOTHING""")
    op.execute("""INSERT INTO role_permissions(role_id, permission_id) SELECT r.id,p.id FROM roles r JOIN permissions p ON p.code IN ('doran.rooms.create','doran.rooms.manage','doran.participants.manage') WHERE r.scope_type='SERVICE' AND r.service_code='doran' AND r.code='room_admin' ON CONFLICT DO NOTHING""")


def downgrade() -> None:
    op.execute("""DO $$ BEGIN
      IF EXISTS (
        SELECT 1 FROM membership_role_assignments a JOIN roles r ON r.id = a.role_id
        WHERE r.scope_type = 'SERVICE' AND r.service_code = 'doran'
          AND r.code IN ('participant','room_admin')
      ) THEN RAISE EXCEPTION 'cannot downgrade Doran while Doran role assignments exist'; END IF;
    END $$""")
    op.execute("""DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE scope_type = 'SERVICE' AND service_code = 'doran' AND code IN ('participant','room_admin'))""")
    op.execute("""DELETE FROM roles WHERE scope_type = 'SERVICE' AND service_code = 'doran' AND code IN ('participant','room_admin')""")
    op.execute("""DELETE FROM permissions WHERE code IN ('doran.rooms.create','doran.rooms.manage','doran.participants.manage','doran.messages.read','doran.messages.send')""")
    op.drop_table("doran_participant_read_states"); op.drop_index("ix_doran_messages_room_sequence", table_name="doran_messages"); op.drop_table("doran_messages"); op.drop_index("ix_doran_participants_room_status", table_name="doran_participants"); op.drop_index("uq_doran_active_participant", table_name="doran_participants"); op.drop_table("doran_participants"); op.drop_index("uq_doran_active_direct_pair", table_name="doran_direct_pairs"); op.drop_table("doran_direct_pairs"); op.drop_table("doran_rooms"); op.drop_constraint("uq_family_memberships_id_family", "family_memberships", type_="unique")
