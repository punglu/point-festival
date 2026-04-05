from datetime import datetime
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime, func
from app.models.base import Base, SoftDeleteMixin


class ChatMessage(Base, SoftDeleteMixin):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
