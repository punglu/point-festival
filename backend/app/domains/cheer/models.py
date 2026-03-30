from sqlalchemy import Column, String, Integer, Date, Text
from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class CheerMessage(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "cheer_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    sender = Column(String(20), nullable=False)  # 'dad' | 'mom'
    message = Column(Text, nullable=False)
