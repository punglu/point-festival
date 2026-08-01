"""Generic Transactional Outbox: any owning-service business transaction can
append a row here in the same DB transaction as its own commit, and a
dedicated Worker later delivers it exactly once, logically, to whichever
downstream consumer owns that event_type (today: Wagle SERVICE_ACTION).

This table has no knowledge of Wagle, Family, or any other consumer - it only
knows an event happened, who owns it, and what has been tried so far.
"""
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base, TimestampMixin


class ServiceOutboxEvent(Base, TimestampMixin):
    __tablename__ = "service_outbox_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_service = Column(String(50), nullable=False)
    event_type = Column(String(60), nullable=False)
    event_version = Column(Integer, nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    aggregate_id = Column(String(64), nullable=False)
    source_event_id = Column(String(128), nullable=False)
    family_id = Column(Integer, nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(String(20), nullable=False, server_default="PENDING")
    attempt_count = Column(Integer, nullable=False, server_default="0")
    next_attempt_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    locked_until = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    last_error_code = Column(String(60), nullable=True)

    __table_args__ = (
        UniqueConstraint("owner_service", "source_event_id", name="uq_service_outbox_owner_source_event"),
        CheckConstraint("status IN ('PENDING', 'PROCESSING', 'PUBLISHED', 'DEAD')", name="ck_service_outbox_status"),
    )
