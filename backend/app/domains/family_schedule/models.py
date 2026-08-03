"""W7.5 Phase D SLICE-SCHEDULE (1g/1o/2u). Fresh table, no legacy relation."""
from sqlalchemy import (
    BigInteger, CheckConstraint, Column, DateTime, ForeignKey,
    ForeignKeyConstraint, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base, TimestampMixin


class FamilyScheduleEvent(Base, TimestampMixin):
    __tablename__ = "family_schedule_events"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    created_by_membership_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200), nullable=True)
    memo = Column(Text, nullable=True)
    # Bounded list of FamilyMembership ids (family size capped at 8) -- not a
    # join table, same shape as `markpoint_missions.checklist`.
    attendee_membership_ids = Column(JSONB, nullable=True)
    visibility = Column(String(20), nullable=False, server_default="family")
    __table_args__ = (
        CheckConstraint("visibility IN ('family', 'private')", name="ck_family_schedule_event_visibility"),
        ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_schedule_event_creator_family", ondelete="RESTRICT",
        ),
    )
