"""W7.5 Phase D — SLICE-ALBUM-METADATA (1h/1p/1w/2y, 앨범).

**Metadata only — no binary upload.** `Photo` rows carry `caption`/
`taken_at`/`uploaded_by_membership_id`, never an image file or URL: no
storage abstraction exists anywhere in `backend/app` (Phase 0/C finding,
same gate as `2v`/avatar upload). `2v` (앨범 업로드 진행) itself is not part
of this Slice and stays `POLICY_BLOCKED`.

`shared_with_membership_ids` (nullable JSONB, `NULL` = shared with the
whole Family, a bounded list = restricted to those members) backs `2y`'s
per-member visibility toggles — bounded by family size (capped at 8),
same shape as `family_schedule_events.attendee_membership_ids`.

Revision ID: 0017_family_album
Revises: 0016_family_schedule
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0017_family_album"
down_revision = "0016_family_schedule"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "family_albums",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("created_by_membership_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("shared_with_membership_ids", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_album_creator_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_family_albums_family", "family_albums", ["family_group_id"])

    op.create_table(
        "family_album_photos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("album_id", sa.BigInteger(), sa.ForeignKey("family_albums.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_group_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_membership_id", sa.Integer(), nullable=False),
        sa.Column("caption", sa.String(length=200), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["family_group_id"], ["family_groups.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["uploaded_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_album_photo_uploader_family", ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_family_album_photos_album", "family_album_photos", ["album_id"])
    op.create_index("ix_family_album_photos_family", "family_album_photos", ["family_group_id"])


def downgrade() -> None:
    op.drop_index("ix_family_album_photos_family", table_name="family_album_photos")
    op.drop_index("ix_family_album_photos_album", table_name="family_album_photos")
    op.drop_table("family_album_photos")
    op.drop_index("ix_family_albums_family", table_name="family_albums")
    op.drop_table("family_albums")
