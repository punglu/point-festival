"""Fresh Wave 5 Markpoint product persistence.

These tables intentionally do not alter legacy player-owned Mission or point
tables.  A FamilyMembership is the only human identity in this aggregate.
"""
from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base, TimestampMixin


class MarkpointMissionTemplate(Base, TimestampMixin):
    __tablename__ = "markpoint_mission_templates"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    assignee_membership_id = Column(Integer, nullable=False)
    created_by_membership_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    reward_amount = Column(Integer, nullable=False)
    cycle_type = Column(String(20), nullable=False, server_default="weekly")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, server_default="active")
    __table_args__ = (
        CheckConstraint("reward_amount >= 0", name="ck_markpoint_template_reward_nonnegative"),
        CheckConstraint("day_of_week IS NULL OR day_of_week BETWEEN 0 AND 6", name="ck_markpoint_template_day"),
        CheckConstraint("status IN ('active', 'cancelled')", name="ck_markpoint_template_status"),
        CheckConstraint("cycle_type IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')", name="ck_markpoint_template_cycle"),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_markpoint_template_date_range"),
        ForeignKeyConstraint(["assignee_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_template_assignee_family", ondelete="RESTRICT"),
        ForeignKeyConstraint(["created_by_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_template_creator_family", ondelete="RESTRICT"),
    )


class MarkpointMission(Base, TimestampMixin):
    __tablename__ = "markpoint_missions"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    assignee_membership_id = Column(Integer, nullable=False)
    created_by_membership_id = Column(Integer, nullable=False)
    approved_by_membership_id = Column(Integer, nullable=True)
    template_id = Column(BigInteger, ForeignKey("markpoint_mission_templates.id", ondelete="RESTRICT"), nullable=True)
    scheduled_for = Column(Date, nullable=False)
    title = Column(String(200), nullable=False)
    reward_amount = Column(Integer, nullable=False)
    status = Column(String(24), nullable=False, server_default="active")
    rejection_reason = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        CheckConstraint("reward_amount >= 0", name="ck_markpoint_mission_reward_nonnegative"),
        CheckConstraint("status IN ('active', 'pending_approval', 'completed', 'rejected', 'cancelled', 'expired')", name="ck_markpoint_mission_status"),
        UniqueConstraint("template_id", "scheduled_for", name="uq_markpoint_mission_template_date"),
        ForeignKeyConstraint(["assignee_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_mission_assignee_family", ondelete="RESTRICT"),
        ForeignKeyConstraint(["created_by_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_mission_creator_family", ondelete="RESTRICT"),
        ForeignKeyConstraint(["approved_by_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_mission_approver_family", ondelete="RESTRICT"),
    )


class MarkpointLedgerEntry(Base):
    __tablename__ = "markpoint_ledger_entries"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    family_membership_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    entry_type = Column(String(32), nullable=False)
    source_type = Column(String(40), nullable=False)
    source_identifier = Column(String(128), nullable=False)
    idempotency_key = Column(String(160), nullable=False)
    reversal_of_entry_id = Column(BigInteger, ForeignKey("markpoint_ledger_entries.id", ondelete="RESTRICT"), nullable=True)
    created_by_membership_id = Column(Integer, nullable=True)
    reason = Column(String(300), nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=False, server_default="{}")
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint("amount <> 0", name="ck_markpoint_ledger_amount_nonzero"),
        CheckConstraint("entry_type IN ('MISSION_REWARD', 'MANUAL_CREDIT', 'MANUAL_DEBIT', 'REVERSAL', 'CORRECTION')", name="ck_markpoint_ledger_entry_type"),
        UniqueConstraint("family_group_id", "idempotency_key", name="uq_markpoint_ledger_family_idempotency"),
        ForeignKeyConstraint(["family_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_ledger_member_family", ondelete="RESTRICT"),
        ForeignKeyConstraint(["created_by_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_ledger_actor_family", ondelete="RESTRICT"),
    )


class MarkpointBalanceProjection(Base, TimestampMixin):
    __tablename__ = "markpoint_balance_projections"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    family_membership_id = Column(Integer, nullable=False)
    current_balance = Column(Integer, nullable=False, server_default="0")
    lifetime_earned = Column(Integer, nullable=False, server_default="0")
    lifetime_spent = Column(Integer, nullable=False, server_default="0")
    version = Column(Integer, nullable=False, server_default="0")
    __table_args__ = (
        UniqueConstraint("family_group_id", "family_membership_id", name="uq_markpoint_balance_family_member"),
        CheckConstraint("lifetime_earned >= 0 AND lifetime_spent >= 0 AND version >= 0", name="ck_markpoint_balance_nonnegative"),
        ForeignKeyConstraint(["family_membership_id", "family_group_id"], ["family_memberships.id", "family_memberships.family_group_id"], name="fk_markpoint_balance_member_family", ondelete="RESTRICT"),
    )


class MarkpointAuditEvent(Base):
    __tablename__ = "markpoint_audit_events"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    actor_membership_id = Column(Integer, nullable=True)
    action = Column(String(60), nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    aggregate_id = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False, server_default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MarkpointFamilyConfig(Base, TimestampMixin):
    """Per-Family Markpoint operating configuration (MP-S04).

    Deliberately **not** the legacy global `configs` row. Legacy stored
    `point_cycle` once for the whole installation; on Mongle a FamilyGroup owns
    its own Markpoint instance, so one Family changing its cycle must not move
    another Family's period boundaries. That is the entire reason this table
    exists rather than a reused global key/value row.

    `cycle_type` repeats the legacy value set exactly — daily, weekly,
    biweekly, monthly, quarterly, yearly — because the range arithmetic in
    `mission/service.get_cycle_range` is the behaviour being preserved, not
    re-invented. Adding a seventh value here without adding it there would
    produce a cycle whose period cannot be computed.
    """

    __tablename__ = "markpoint_family_configs"

    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    cycle_type = Column(String(20), nullable=False, server_default="weekly")
    # The cycle period this configuration is in force for. Guard A compares
    # "today" against `effective_to`: while the current period is still
    # running, its own boundaries cannot be moved out from under the missions
    # already scheduled inside it.
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=False)
    display_name = Column(String(100), nullable=True)
    updated_by_membership_id = Column(Integer, nullable=True)

    __table_args__ = (
        # One configuration per Family. A second row would make "the current
        # cycle" ambiguous, and every guard below depends on it being singular.
        UniqueConstraint("family_group_id", name="uq_markpoint_family_config_family"),
        CheckConstraint(
            "cycle_type IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')",
            name="ck_markpoint_family_config_cycle",
        ),
        CheckConstraint("effective_to >= effective_from", name="ck_markpoint_family_config_range"),
        ForeignKeyConstraint(
            ["updated_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_markpoint_family_config_actor_family",
            ondelete="RESTRICT",
        ),
    )
