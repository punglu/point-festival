from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class MissionTemplate(Base, SoftDeleteMixin, TimestampMixin):
    """반복 미션 템플릿. day_of_week는 비트마스크 (1=월~64=일, 127=매일)"""
    __tablename__ = "mission_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(500), nullable=False)
    point = Column(Integer, default=0, nullable=False)
    day_of_week = Column(Integer, default=127, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_generated_date = Column(Date, nullable=True)
    group_id            = Column(String(36), nullable=True)
