"""W7.5 Phase C: additive profile fields (Account) and mission detail fields
(MarkpointMission).

All columns are nullable/no-default-change and purely additive — no existing
column is altered, no data is backfilled or migrated. Each column closes one
Matrix Phase C gap:

- `accounts.bio` / `birthday` / `avatar_color`: 2z (profile edit) has no
  backing storage for these fields today. `display_name` already existed.
- `markpoint_missions.description` / `checklist`: 1k (mission detail) needs a
  free-text description and a structured checklist; neither existed.
  `rejection_reason` is NOT added here — it already exists (0010) and was
  simply never exposed in `MissionOut`, a schema-only fix.

Revision ID: 0012_profile_mission_fields (kept <=32 chars for
`alembic_version.version_num` -- see 0011's own note on this exact trap)
Revises: 0011_markpoint_family_config
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0012_profile_mission_fields"
down_revision = "0011_markpoint_family_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("bio", sa.String(length=200), nullable=True))
    op.add_column("accounts", sa.Column("birthday", sa.Date(), nullable=True))
    op.add_column("accounts", sa.Column("avatar_color", sa.String(length=7), nullable=True))

    op.add_column("markpoint_missions", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("markpoint_missions", sa.Column("checklist", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("markpoint_missions", "checklist")
    op.drop_column("markpoint_missions", "description")

    op.drop_column("accounts", "avatar_color")
    op.drop_column("accounts", "birthday")
    op.drop_column("accounts", "bio")
