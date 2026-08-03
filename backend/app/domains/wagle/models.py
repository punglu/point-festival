"""Persistence boundaries for secure, Family-scoped Wagle messaging.

These tables deliberately do not reuse legacy ``chat_messages``.  Account,
Service, and System message actors are structurally distinct.
"""
from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey, ForeignKeyConstraint, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from app.models.base import Base, SoftDeleteMixin, TimestampMixin
from app.domains.wagle.board_constants import FAMILY_BOARD_ROOM_TITLE


class WagleRoom(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "wagle_rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    room_type = Column(String(20), nullable=False)
    title = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, server_default="active")
    created_by_actor_type = Column(String(20), nullable=False)
    created_by_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    next_message_sequence = Column(BigInteger, nullable=False, server_default="0")
    version = Column(Integer, nullable=False, server_default="1")
    closed_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        UniqueConstraint("id", "family_group_id", name="uq_wagle_rooms_id_family"),
        CheckConstraint("room_type IN ('DIRECT', 'GROUP', 'SERVICE')", name="ck_wagle_rooms_type"),
        CheckConstraint("status IN ('active', 'read_only', 'closed', 'deleted')", name="ck_wagle_rooms_status"),
        CheckConstraint("created_by_actor_type IN ('ACCOUNT', 'SERVICE', 'SYSTEM')", name="ck_wagle_rooms_actor"),
    )


class WagleDirectPair(Base):
    __tablename__ = "wagle_direct_pairs"
    room_id = Column(UUID(as_uuid=True), ForeignKey("wagle_rooms.id", ondelete="RESTRICT"), primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    membership_low_id = Column(Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False)
    membership_high_id = Column(Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint("membership_low_id < membership_high_id", name="ck_wagle_direct_pair_order"),
        ForeignKeyConstraint(["membership_low_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], ondelete="RESTRICT"),
        ForeignKeyConstraint(["membership_high_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], ondelete="RESTRICT"),
    )


class WagleParticipant(Base, TimestampMixin):
    __tablename__ = "wagle_participants"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    family_group_id = Column(Integer, nullable=False)
    room_id = Column(UUID(as_uuid=True), nullable=False)
    family_membership_id = Column(Integer, nullable=False)
    room_role = Column(String(20), nullable=False, server_default="member")
    status = Column(String(20), nullable=False, server_default="active")
    joined_sequence = Column(BigInteger, nullable=False)
    left_sequence = Column(BigInteger, nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    removed_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(["room_id", "family_group_id"], ["wagle_rooms.id", "wagle_rooms.family_group_id"], ondelete="RESTRICT"),
        ForeignKeyConstraint(["family_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], ondelete="RESTRICT"),
        CheckConstraint("room_role IN ('room_admin', 'member')", name="ck_wagle_participants_role"),
        CheckConstraint("status IN ('active', 'left', 'removed')", name="ck_wagle_participants_status"),
        CheckConstraint("left_sequence IS NULL OR left_sequence >= joined_sequence", name="ck_wagle_participants_sequence_range"),
    )


Index(
    # Migration 0021. Only the reserved family-board sentinel gets a DB
    # invariant -- ordinary GROUP rooms may still legitimately share a
    # display title, so this is deliberately not a bare (family_group_id,
    # title) unique constraint.
    "uq_wagle_rooms_family_board_singleton",
    WagleRoom.family_group_id,
    unique=True,
    postgresql_where=(WagleRoom.room_type == "GROUP") & (WagleRoom.title == FAMILY_BOARD_ROOM_TITLE) & WagleRoom.deleted_at.is_(None),
)
Index(
    "uq_wagle_active_direct_pair",
    WagleDirectPair.family_group_id,
    WagleDirectPair.membership_low_id,
    WagleDirectPair.membership_high_id,
    unique=True,
    postgresql_where=WagleDirectPair.is_active.is_(True),
)
Index(
    "uq_wagle_active_participant",
    WagleParticipant.room_id,
    WagleParticipant.family_membership_id,
    unique=True,
    postgresql_where=WagleParticipant.status == "active",
)
Index("ix_wagle_participants_room_status", WagleParticipant.room_id, WagleParticipant.status)


class WagleMessage(Base):
    __tablename__ = "wagle_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    family_group_id = Column(Integer, nullable=False)
    room_id = Column(UUID(as_uuid=True), nullable=False)
    sequence = Column(BigInteger, nullable=False)
    sender_participant_id = Column(UUID(as_uuid=True), ForeignKey("wagle_participants.id", ondelete="RESTRICT"), nullable=True)
    message_type = Column(String(20), nullable=False, server_default="TEXT")
    client_message_id = Column(String(64), nullable=True)
    body = Column(Text, nullable=True)
    reply_to_message_id = Column(UUID(as_uuid=True), nullable=True)
    service_code = Column(String(50), nullable=True)
    service_payload_version = Column(Integer, nullable=True)
    service_payload = Column(JSONB, nullable=True)
    service_principal_id = Column(Integer, ForeignKey("service_principals.id", ondelete="RESTRICT"), nullable=True)
    source = Column(String(100), nullable=True)
    source_event_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by_account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(["room_id", "family_group_id"], ["wagle_rooms.id", "wagle_rooms.family_group_id"], ondelete="RESTRICT"),
        UniqueConstraint("room_id", "sequence", name="uq_wagle_messages_room_sequence"),
        UniqueConstraint("sender_participant_id", "room_id", "client_message_id", name="uq_wagle_messages_sender_client"),
        CheckConstraint("message_type IN ('TEXT', 'SYSTEM', 'SERVICE_ACTION')", name="ck_wagle_messages_type"),
        CheckConstraint("(message_type = 'TEXT' AND body IS NOT NULL AND length(body) BETWEEN 1 AND 4000) OR message_type <> 'TEXT'", name="ck_wagle_messages_text_body"),
        # A Service Principal must never be attributable as a human sender, and a
        # human/system message must never carry a Service Principal identity -
        # this is the DB-level backstop for "service cannot impersonate a user".
        CheckConstraint(
            "(message_type = 'SERVICE_ACTION' AND service_principal_id IS NOT NULL AND sender_participant_id IS NULL "
            "AND service_code IS NOT NULL AND source IS NOT NULL AND source_event_id IS NOT NULL) "
            "OR (message_type <> 'SERVICE_ACTION' AND service_principal_id IS NULL AND source IS NULL AND source_event_id IS NULL)",
            name="ck_wagle_messages_service_actor",
        ),
    )


class WagleParticipantReadState(Base):
    __tablename__ = "wagle_participant_read_states"
    participant_id = Column(UUID(as_uuid=True), ForeignKey("wagle_participants.id", ondelete="RESTRICT"), primary_key=True)
    last_read_sequence = Column(BigInteger, nullable=False, server_default="0")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    __table_args__ = (CheckConstraint("last_read_sequence >= 0", name="ck_wagle_read_state_nonnegative"),)


class ServicePrincipal(Base, TimestampMixin):
    """An Attached Service's own identity - never a user Account, never a JWT.

    Only ``credential_hash`` is persisted; the plaintext secret is returned to
    the caller exactly once at issuance and is not recoverable afterward.
    """
    __tablename__ = "service_principals"
    id = Column(Integer, primary_key=True)
    service_code = Column(String(50), nullable=False)
    display_name = Column(String(100), nullable=False)
    credential_id = Column(String(64), nullable=False, unique=True)
    credential_hash = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, server_default="active")
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (CheckConstraint("status IN ('active', 'revoked')", name="ck_service_principals_status"),)


class WagleServiceBinding(Base, TimestampMixin):
    """The only source of Service-publish authority: a Principal is bound to
    exactly one Room in one Family with an explicit action allowlist. Family
    service subscription, Room admin, and this Binding are evaluated together
    and none of the three substitutes for another."""
    __tablename__ = "wagle_service_bindings"
    id = Column(Integer, primary_key=True)
    service_principal_id = Column(Integer, ForeignKey("service_principals.id", ondelete="RESTRICT"), nullable=False)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    room_id = Column(UUID(as_uuid=True), nullable=False)
    allowed_actions = Column(JSONB, nullable=False)
    status = Column(String(20), nullable=False, server_default="active")
    __table_args__ = (
        ForeignKeyConstraint(["room_id", "family_group_id"], ["wagle_rooms.id", "wagle_rooms.family_group_id"], ondelete="RESTRICT"),
        UniqueConstraint("service_principal_id", "room_id", name="uq_wagle_service_binding_principal_room"),
        CheckConstraint("status IN ('active', 'inactive')", name="ck_wagle_service_bindings_status"),
    )


class WagleServiceAuditLog(Base):
    """Minimal audit trail: identifiers and a result code only - never a
    credential, token, message body, or full Action payload. family_group_id
    and room_id are intentionally NOT foreign keys, so a denied attempt against
    a nonexistent/foreign Family or Room can still be recorded."""
    __tablename__ = "wagle_service_audit_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_type = Column(String(40), nullable=False)
    service_principal_id = Column(Integer, ForeignKey("service_principals.id", ondelete="RESTRICT"), nullable=True)
    family_group_id = Column(Integer, nullable=True)
    room_id = Column(UUID(as_uuid=True), nullable=True)
    result_code = Column(String(20), nullable=False)
    detail = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('principal_created','principal_revoked','binding_created','binding_activated',"
            "'binding_deactivated','publish_success','replay_detected','permission_denied','schema_denied')",
            name="ck_wagle_service_audit_event_type",
        ),
    )


class WagleMessageReaction(Base):
    """W7.5 Phase D SLICE-WAGLE-BOARD-REACTIONS (3e). A single boolean-style
    reaction (toggle on/off) per (message, reactor) -- matches exactly what
    the frozen 3c/3e canonical Screens render (one heart icon, no
    reaction-type picker), so no multi-emoji taxonomy is invented here."""
    __tablename__ = "wagle_message_reactions"
    id = Column(BigInteger, primary_key=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("wagle_messages.id", ondelete="CASCADE"), nullable=False)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    reactor_membership_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("message_id", "reactor_membership_id", name="uq_wagle_message_reaction_actor"),
    )


Index("ix_wagle_messages_room_sequence", WagleMessage.room_id, WagleMessage.sequence)
Index(
    "uq_wagle_messages_service_idempotency",
    WagleMessage.service_principal_id,
    WagleMessage.source,
    WagleMessage.source_event_id,
    unique=True,
    postgresql_where=WagleMessage.message_type == "SERVICE_ACTION",
)
Index("ix_wagle_service_bindings_principal", WagleServiceBinding.service_principal_id)
Index("ix_wagle_service_audit_log_principal_created", WagleServiceAuditLog.service_principal_id, WagleServiceAuditLog.created_at)
