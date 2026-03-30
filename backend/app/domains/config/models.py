from sqlalchemy import Column, String, Integer, Text
from app.models.base import Base, TimestampMixin

# app_configs에는 deleted_at 없음 (init.sql 기준) — SoftDeleteMixin 미적용


class AppConfig(Base, TimestampMixin):
    __tablename__ = "app_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=True)
