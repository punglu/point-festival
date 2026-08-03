"""W7.5 Phase D SLICE-REWARD-CATALOG (1l/2h/2j). Fresh tables."""
from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    ForeignKeyConstraint, Integer, String, func,
)
from app.models.base import Base, TimestampMixin


class RewardCatalogItem(Base, TimestampMixin):
    __tablename__ = "reward_catalog_items"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    created_by_membership_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    cost = Column(Integer, nullable=False)
    is_available = Column(Boolean, nullable=False, server_default="true")
    __table_args__ = (
        CheckConstraint("cost >= 0", name="ck_reward_catalog_item_cost_nonnegative"),
        ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_reward_catalog_item_creator_family", ondelete="RESTRICT",
        ),
    )


class RewardRedemption(Base):
    __tablename__ = "reward_redemptions"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    reward_item_id = Column(BigInteger, ForeignKey("reward_catalog_items.id", ondelete="RESTRICT"), nullable=False)
    redeemed_by_membership_id = Column(Integer, nullable=False)
    cost_at_redemption = Column(Integer, nullable=False)
    ledger_entry_id = Column(BigInteger, ForeignKey("markpoint_ledger_entries.id", ondelete="RESTRICT"), nullable=False)
    redeemed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["redeemed_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_reward_redemption_redeemer_family", ondelete="RESTRICT",
        ),
    )
