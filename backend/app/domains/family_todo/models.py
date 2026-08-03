"""W7.5 Phase D SLICE-TODO (1i). Fresh table, no legacy relation."""
from sqlalchemy import (
    BigInteger, CheckConstraint, Column, DateTime, ForeignKey,
    ForeignKeyConstraint, Integer, String,
)
from app.models.base import Base, TimestampMixin


class FamilyTodo(Base, TimestampMixin):
    __tablename__ = "family_todos"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    assignee_membership_id = Column(Integer, nullable=True)
    created_by_membership_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, server_default="open")
    due_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        CheckConstraint("status IN ('open', 'done')", name="ck_family_todo_status"),
        ForeignKeyConstraint(
            ["assignee_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_todo_assignee_family", ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_todo_creator_family", ondelete="RESTRICT",
        ),
    )
