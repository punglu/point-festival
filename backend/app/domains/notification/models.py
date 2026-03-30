from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, func
from sqlalchemy.types import TIMESTAMP
from app.models.base import Base, SoftDeleteMixin

# notifications 테이블에는 updated_at이 없음 (init.sql 기준)


class Notification(Base, SoftDeleteMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(30), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
