from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.domains.config.schema import ConfigUpdate, ConfigResponse
from app.domains.config.service import get_all_configs, get_config_by_key, upsert_config

router = APIRouter(prefix="/api/configs", tags=["Config"])


@router.get("/", response_model=list[ConfigResponse])
async def list_configs(
    _: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """전체 앱 설정 조회"""
    return await get_all_configs(db)


@router.get("/{key}", response_model=ConfigResponse)
async def get_config(
    key: str,
    _: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """키로 설정값 조회"""
    return await get_config_by_key(db, key)


@router.put("/{key}", response_model=ConfigResponse)
async def save_config(
    key: str,
    data: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """설정값 저장 (Upsert)"""
    return await upsert_config(db, key, data)
