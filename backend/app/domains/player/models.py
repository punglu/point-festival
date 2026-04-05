from sqlalchemy import Boolean, Column, String, Integer, BigInteger, Text, CheckConstraint
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Player(Base, SoftDeleteMixin, TimestampMixin):
    """플레이어(아이) 프로필
    Firebase 원본: mc_players/{playerId}
    Gemini C-4: role 필드 (RBAC)
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    role = Column(
        String(10),
        nullable=False,
        default="player",
        server_default="player",
    )
    photo = Column(Text, nullable=True)
    status_msg = Column(String(200), nullable=True)
    last_login = Column(BigInteger, nullable=True)
    is_locked            = Column(Boolean, default=False, nullable=False, server_default="false")
    is_visible           = Column(Boolean, default=True,  nullable=False, server_default="true")
    is_dashboard_visible = Column(Boolean, default=True,  nullable=False, server_default="true")

    __table_args__ = (
        CheckConstraint("role IN ('player', 'admin')", name="ck_player_role"),
    )
