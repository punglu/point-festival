from sqlalchemy import Boolean, Column, String, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class PlayerAuth(Base, SoftDeleteMixin, TimestampMixin):
    """플레이어 인증 정보 (PIN, 잠금 상태)
    Firebase 원본: mc_player_auth/{playerId}
    """
    __tablename__ = "player_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    pin_hash = Column(String(128), nullable=False)
    login_attempts = Column(Integer, default=0, nullable=False)
    lock_until = Column(BigInteger, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False, server_default="false")


class AdminAuth(Base, SoftDeleteMixin):
    """관리자 ID/PW 인증 정보"""
    __tablename__ = "admin_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    display_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
