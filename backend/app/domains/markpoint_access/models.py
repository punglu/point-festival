"""Markpoint access-control persistence (Wave 4, D5-A3 / D5-B).

Two pieces of state the generic `service_subscriptions` + RBAC tables cannot
express: a member-initiated activation request awaiting FamilyAdmin approval,
and an explicit per-member restriction that overrides default access.

Neither is a `MarkpointParticipant` aggregate. Default access stays derived per
request from `ServiceSubscription` + `FamilyMembership`; a restriction row is a
*subtraction* from that, and its absence is the normal state.
"""
from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String, func,
)

from app.models.base import Base, TimestampMixin

SERVICE_CODE = "markpoint"


class MarkpointActivationRequest(Base, TimestampMixin):
    __tablename__ = "markpoint_activation_requests"

    id = Column(Integer, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    service_code = Column(String(50), nullable=False, default=SERVICE_CODE, server_default=SERVICE_CODE)
    requester_membership_id = Column(
        Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False
    )
    status = Column(String(20), nullable=False, default="PENDING", server_default="PENDING")
    processed_by_membership_id = Column(
        Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=True
    )
    requested_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    decision_note = Column(String(300), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')",
            name="ck_markpoint_activation_requests_status",
        ),
        CheckConstraint(
            "(status = 'PENDING' AND processed_at IS NULL AND processed_by_membership_id IS NULL) "
            "OR (status <> 'PENDING' AND processed_at IS NOT NULL)",
            name="ck_markpoint_activation_requests_processed",
        ),
    )


class MarkpointAccessRestriction(Base, TimestampMixin):
    __tablename__ = "markpoint_access_restrictions"

    id = Column(Integer, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    service_code = Column(String(50), nullable=False, default=SERVICE_CODE, server_default=SERVICE_CODE)
    target_membership_id = Column(
        Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False
    )
    status = Column(String(20), nullable=False, default="ACTIVE", server_default="ACTIVE")
    reason = Column(String(300), nullable=True)
    restricted_by_membership_id = Column(
        Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=False
    )
    restricted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    restored_by_membership_id = Column(
        Integer, ForeignKey("family_memberships.id", ondelete="RESTRICT"), nullable=True
    )
    restored_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'RESTORED')", name="ck_markpoint_access_restrictions_status"),
        CheckConstraint(
            "(status = 'ACTIVE' AND restored_at IS NULL AND restored_by_membership_id IS NULL) "
            "OR (status = 'RESTORED' AND restored_at IS NOT NULL)",
            name="ck_markpoint_access_restrictions_restored",
        ),
        # Mirrors the wagle_participants pattern: a restriction can only target a
        # membership of the same family, enforced by the DB rather than by
        # application code alone.
        ForeignKeyConstraint(
            ["target_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            ondelete="RESTRICT",
            name="fk_markpoint_restriction_target_family",
        ),
    )
