"""W7.5 Phase D — SLICE-WAGLE-BOARD-REACTIONS (3e, 인기 게시글).

Resolved as IMPLEMENTATION_REQUIRED, not a PM policy gate: the reaction
concept is already fully determined by the existing frozen canonical
Screens themselves -- both `3c` (가족 게시판) and `3e` display
`♥ {likes} · 💬 {comments}` as a core visual element already, so this is
making an already-designed-for stat real, not inventing a new product
concept. A single boolean-style reaction (toggle on/off) matches exactly
what both Screens render -- neither shows more than one reaction type, so
no multi-emoji-reaction taxonomy is invented here.

One row per (message, reactor); reacting again removes it (toggle), which
is what a single heart icon with no reaction-type picker implies.

Revision ID: 0020_wagle_message_reactions
Revises: 0019_account_notification
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0020_wagle_message_reactions"
down_revision = "0019_account_notification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wagle_message_reactions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("message_id", UUID(as_uuid=True), sa.ForeignKey("wagle_messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("reactor_membership_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id", "reactor_membership_id", name="uq_wagle_message_reaction_actor"),
    )
    op.create_index("ix_wagle_message_reactions_message", "wagle_message_reactions", ["message_id"])
    op.create_index("ix_wagle_message_reactions_family", "wagle_message_reactions", ["family_group_id"])


def downgrade() -> None:
    op.drop_index("ix_wagle_message_reactions_family", table_name="wagle_message_reactions")
    op.drop_index("ix_wagle_message_reactions_message", table_name="wagle_message_reactions")
    op.drop_table("wagle_message_reactions")
