from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, DateTime, func
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Feedback(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    msg = Column(Text, nullable=False)


class FeedbackReply(Base, SoftDeleteMixin):
    """feedback_replies는 updated_at 없음 (init.sql 기준) — created_at만 직접 정의"""
    __tablename__ = "feedback_replies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
