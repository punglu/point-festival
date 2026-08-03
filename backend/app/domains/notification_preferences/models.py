"""W7.5 Phase D SLICE-NOTIFICATION-PREFERENCES (2n). Fresh table."""
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from app.models.base import Base, TimestampMixin


class AccountNotificationPreference(Base, TimestampMixin):
    __tablename__ = "account_notification_preferences"
    id = Column(BigInteger, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    pref_key = Column(String(50), nullable=False)
    enabled = Column(Boolean, nullable=False)
    __table_args__ = (UniqueConstraint("account_id", "pref_key", name="uq_account_notification_pref"),)
