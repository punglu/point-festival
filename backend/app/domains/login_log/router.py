from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.login_log.schema import LoginLogResponse
from app.domains.login_log.service import get_login_logs_by_player

router = APIRouter(prefix="/api/login-logs", tags=["LoginLog"])


@router.get("/", response_model=list[LoginLogResponse])
async def list_logs(
    player_id: int = Query(...),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """플레이어의 로그인 이력 조회"""
    return await get_login_logs_by_player(db, player_id, limit)
