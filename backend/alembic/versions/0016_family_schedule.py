"""W7.5 Phase D — SLICE-SCHEDULE (1g/1o/2u, 가족 일정).

One aggregate shared by three screens (list/create/detail-edit-delete),
per the Phase D Slice Mapping. `3a` (캘린더 공유)'s external Google/Apple
Calendar sync and webcal subscription link are **not** part of this table
-- that is a real external-service OAuth/feed-generation integration with
no credentials or infra in this repository, out of this Slice's scope
(same shape as the storage-infra gate). `attendee_membership_ids` is a
JSONB array rather than a join table -- bounded (family size is capped at
8, per the product's own stated limit), and matches the existing
`markpoint_missions.checklist` precedent for a small bounded list on one
row rather than a second table.

Revision ID: 0016_family_schedule
Revises: 0015_notification_prefs
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0016_family_schedule"
down_revision = "0015_notification_prefs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "family_schedule_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("created_by_membership_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("attendee_membership_ids", JSONB, nullable=True),
        sa.Column("visibility", sa.String(length=20), server_default="family", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_schedule_event_creator_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("visibility IN ('family', 'private')", name="ck_family_schedule_event_visibility"),
    )
    op.create_index("ix_family_schedule_events_family", "family_schedule_events", ["family_group_id"])


def downgrade() -> None:
    op.drop_index("ix_family_schedule_events_family", table_name="family_schedule_events")
    op.drop_table("family_schedule_events")
