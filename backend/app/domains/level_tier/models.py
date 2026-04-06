"""Level Tier 모델 — 레벨 구간 정의"""
from sqlalchemy import String, Integer, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base


class LevelTier(Base):
    __tablename__ = "level_tiers"
    __table_args__ = (
        UniqueConstraint("job_code", "level", name="uq_job_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_code: Mapped[str] = mapped_column(String(20), nullable=False, default="COMMON")
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    icon_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    milestone_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    milestone_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
