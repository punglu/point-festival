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


async def validate_cycle_change(db: AsyncSession, new_cycle: str) -> None:
    """
    주기 변경 전 2중 가드 검증. 실패 시 HTTPException(400) raise.

    가드 A: 현재 주기가 아직 진행 중이면 잠금
    가드 B: 활성 반복 미션 템플릿이 존재하면 잠금
    설계 예외: config 도메인에서 mission/mission_template 조회 (PM 승인, 읽기 전용)
    """
    from datetime import date
    from fastapi import HTTPException
    from sqlalchemy import func, select as sa_select
    from app.domains.mission.service import get_cycle_range, get_current_cycle

    today = date.today()
    current_cycle = await get_current_cycle(db)

    if current_cycle == new_cycle:
        return

    # --- 가드 A: 주기 진행 중 잠금 ---
    _, cycle_end = get_cycle_range(current_cycle, today)
    if today <= cycle_end:
        remaining = (cycle_end - today).days
        raise HTTPException(
            status_code=400,
            detail=f"현재 주기({current_cycle}) 종료까지 {remaining}일 남았습니다. "
                   f"{cycle_end.isoformat()} 이후 변경 가능합니다.",
        )

    # --- 가드 B: 활성 반복 미션 의존성 잠금 ---
    from app.domains.mission_template.models import MissionTemplate
    stmt = sa_select(func.count()).select_from(MissionTemplate).where(
        MissionTemplate.is_active.is_(True),
        MissionTemplate.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    template_count = result.scalar() or 0
    if template_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"활성 반복 미션이 {template_count}건 있습니다. "
                   f"반복 미션을 모두 비활성화하거나 삭제한 후 주기를 변경하세요.",
        )


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

    if key == "point_cycle":
        valid_cycles = {"daily", "weekly", "biweekly", "monthly", "quarterly", "yearly"}
        if data.value not in valid_cycles:
            raise HTTPException(
                status_code=400,
                detail=f"유효하지 않은 주기 값: '{data.value}'. 허용값: {valid_cycles}",
            )
        await validate_cycle_change(db, data.value)

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
