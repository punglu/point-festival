from sqlalchemy import Column, String, Integer, Date, ForeignKey
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Deduction(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "deductions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String(300), nullable=False)
    amount = Column(Integer, nullable=False)
