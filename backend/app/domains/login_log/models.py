from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey, func
from sqlalchemy.types import TIMESTAMP
from app.models.base import Base

# login_logs에는 updated_at, deleted_at 없음 (init.sql 기준) — Mixin 미적용


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
