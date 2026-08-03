"""W7.5 Phase D SLICE-NOTIFICATION-LIST (1n). Account-native, not a
`LegacyIdentityMapping` extension -- see the migration's own docstring."""
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, func
from app.models.base import Base


class AccountNotification(Base):
    __tablename__ = "account_notifications"
    id = Column(BigInteger, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    category = Column(String(30), nullable=False, server_default="general")
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
