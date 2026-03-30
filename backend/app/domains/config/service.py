from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.config.models import AppConfig
from app.domains.config.schema import ConfigUpdate, ConfigResponse  # noqa: F401


async def get_all_configs(db: AsyncSession) -> list[ConfigResponse]:
    """
    -- [SQL] 전체 앱 설정 조회
    -- SELECT * FROM app_configs ORDER BY key ASC;
    """
    stmt = select(AppConfig).order_by(AppConfig.key.asc())
    result = await db.execute(stmt)
    return [ConfigResponse.model_validate(r) for r in result.scalars().all()]


async def get_config_by_key(db: AsyncSession, key: str) -> ConfigResponse:
    """
    -- [SQL] 키로 설정값 조회
    -- SELECT * FROM app_configs WHERE key = :key;
    """
    stmt = select(AppConfig).where(AppConfig.key == key)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail=f"설정 키 '{key}'를 찾을 수 없습니다")
    return ConfigResponse.model_validate(config)


async def upsert_config(db: AsyncSession, key: str, data: ConfigUpdate) -> ConfigResponse:
    """
    -- [SQL] 설정값 Upsert
    -- SELECT * FROM app_configs WHERE key = :key;
    -- 존재: UPDATE app_configs SET value = :value, updated_at = NOW() WHERE key = :key;
    -- 미존재: INSERT INTO app_configs (key, value) VALUES (:key, :value);
    """
    stmt = select(AppConfig).where(AppConfig.key == key)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.value = data.value
        await db.commit()
        await db.refresh(existing)
        return ConfigResponse.model_validate(existing)
    else:
        config = AppConfig(key=key, value=data.value)
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return ConfigResponse.model_validate(config)
