from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Mission(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    text = Column(String(500), nullable=False)
    point = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active")
    sender = Column(String(20), nullable=True)
    msg = Column(Text, nullable=True)
    proposed_by = Column(String(20), nullable=True)
    proposal_reason = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    sort_order  = Column(Integer, nullable=False, default=0)
    group_id    = Column(String(36), nullable=True)
    template_id = Column(Integer, ForeignKey("mission_templates.id", ondelete="SET NULL"), nullable=True)
