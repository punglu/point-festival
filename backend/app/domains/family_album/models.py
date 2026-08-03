"""W7.5 Phase D SLICE-ALBUM-METADATA (1h/1p/1w/2y). Metadata only, no binary
upload -- see the migration's own docstring for why."""
from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, ForeignKeyConstraint, Integer,
    String, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base, TimestampMixin


class FamilyAlbum(Base, TimestampMixin):
    __tablename__ = "family_albums"
    id = Column(BigInteger, primary_key=True)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    created_by_membership_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    # NULL = shared with the whole Family; a bounded list restricts visibility (2y).
    shared_with_membership_ids = Column(JSONB, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(
            ["created_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_album_creator_family", ondelete="RESTRICT",
        ),
    )


class FamilyAlbumPhoto(Base):
    __tablename__ = "family_album_photos"
    id = Column(BigInteger, primary_key=True)
    album_id = Column(BigInteger, ForeignKey("family_albums.id", ondelete="CASCADE"), nullable=False)
    family_group_id = Column(Integer, ForeignKey("family_groups.id", ondelete="RESTRICT"), nullable=False)
    uploaded_by_membership_id = Column(Integer, nullable=False)
    caption = Column(String(200), nullable=True)
    taken_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["uploaded_by_membership_id", "family_group_id"],
            ["family_memberships.id", "family_memberships.family_group_id"],
            name="fk_family_album_photo_uploader_family", ondelete="RESTRICT",
        ),
    )
