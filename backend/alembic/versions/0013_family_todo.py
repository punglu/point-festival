"""W7.5 Phase D — SLICE-TODO (1i, 가족 할 일).

Simple, bounded, no policy blocker (Matrix note). A Todo belongs to one
Family; `assignee_membership_id` is nullable for a family-wide chore with
no single owner. No point/reward integration — completing a Todo does not
touch the Markpoint Ledger; that would be a business-rule decision this
task does not have authority to invent (same discipline as `2c`'s bonus
question).

Revision ID: 0013_family_todo
Revises: 0012_profile_mission_fields
"""
from alembic import op
import sqlalchemy as sa

revision = "0013_family_todo"
down_revision = "0012_profile_mission_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "family_todos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("assignee_membership_id", sa.Integer(), nullable=True),
        sa.Column("created_by_membership_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="open", nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["assignee_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_todo_assignee_family", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_todo_creator_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('open', 'done')", name="ck_family_todo_status"),
    )
    op.create_index("ix_family_todos_family", "family_todos", ["family_group_id"])


def downgrade() -> None:
    op.drop_index("ix_family_todos_family", table_name="family_todos")
    op.drop_table("family_todos")
