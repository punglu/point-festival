"""미션 템플릿 라우터 — Admin 전용"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.auth.dependencies import get_current_admin
from app.domains.mission_template import service as template_service
from app.domains.mission_template.schema import (
    MissionTemplateCreate,
    MissionTemplateUpdate,
    MissionTemplateResponse,
)

router = APIRouter(prefix="/api/mission-templates", tags=["mission-templates"])


@router.get("", response_model=list[MissionTemplateResponse])
async def list_templates(
    player_id: int | None = None,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await template_service.list_templates(db, player_id)


@router.post("", response_model=MissionTemplateResponse, status_code=201)
async def create_template(
    data: MissionTemplateCreate,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await template_service.create_template(db, data)
    await db.commit()
    return result


@router.patch("/{template_id}", response_model=MissionTemplateResponse)
async def update_template(
    template_id: int,
    data: MissionTemplateUpdate,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await template_service.update_template(db, template_id, data)
    await db.commit()
    return result


@router.delete("/by-group/{group_id}", status_code=204)
async def delete_templates_by_group(
    group_id: str,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """group_id가 같은 템플릿 전체 삭제 (각 템플릿은 cascade로 관련 미션도 정리)"""
    await template_service.delete_templates_by_group(db, group_id)
    await db.commit()


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await template_service.delete_template(db, template_id)
    await db.commit()


@router.post("/generate", status_code=200)
async def generate_today(
    _admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    관리자 대시보드 진입 시 호출.
    롤링 윈도우(오늘~다음주 일요일) 범위 전체 미션 생성.
    """
    start, end = template_service.get_rolling_window()
    count = await template_service.generate_missions_for_range(db, start, end)
    await db.commit()
    return {"generated": count, "range": f"{start} ~ {end}"}
