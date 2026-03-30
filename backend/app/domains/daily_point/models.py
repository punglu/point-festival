from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class DailyPoint(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "daily_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    earned = Column(Integer, nullable=False, default=0)
    spent = Column(Integer, nullable=False, default=0)
    balance = Column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("player_id", "date"),)
