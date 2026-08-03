"""W7.5 Phase D SLICE-FAMILY-RULES (1v). Fresh table, no legacy relation."""
from sqlalchemy import (
    BigInteger, CheckConstraint, Column, ForeignKey, ForeignKeyConstraint,
    Integer, String,
)
from app.models.base import Base, TimestampMixin


class FamilyRule(Base, TimestampMixin):
    __tablename__ = "family_rules"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    category = Column(String(20), nullable=False)
    label = Column(String(100), nullable=False)
    value_text = Column(String(200), nullable=False)
    sort_order = Column(Integer, nullable=False, server_default="0")
    updated_by_membership_id = Column(Integer, nullable=True)
    __table_args__ = (
        CheckConstraint("category IN ('life', 'point')", name="ck_family_rule_category"),
        ForeignKeyConstraint(
            ["updated_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_rule_actor_family", ondelete="RESTRICT",
        ),
    )
