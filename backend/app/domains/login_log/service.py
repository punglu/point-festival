from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.login_log.models import LoginLog
from app.domains.login_log.schema import LoginLogCreate, LoginLogResponse


async def get_all_login_logs(
    db: AsyncSession,
    player_id: Optional[int] = None,
    limit: int = 50,
) -> list[LoginLogResponse]:
    """
    -- [SQL] Admin 전체 로그인 이력 조회 (player_id 선택 필터)
    -- SELECT * FROM login_logs
    -- [WHERE player_id = :player_id]
    -- ORDER BY created_at DESC LIMIT :limit;
    """
    stmt = select(LoginLog)
    if player_id is not None:
        stmt = stmt.where(LoginLog.player_id == player_id)
    stmt = stmt.order_by(LoginLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return [LoginLogResponse.model_validate(log) for log in result.scalars().all()]


async def get_login_logs_by_player(
    db: AsyncSession, player_id: int, limit: int = 50
) -> list[LoginLogResponse]:
    """
    -- [SQL] 플레이어의 로그인 이력 조회 (최근 N건)
    -- SELECT * FROM login_logs
    -- WHERE player_id = :player_id
    -- ORDER BY created_at DESC LIMIT :limit;
    """
    stmt = (
        select(LoginLog)
        .where(LoginLog.player_id == player_id)
        .order_by(LoginLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [LoginLogResponse.model_validate(r) for r in result.scalars().all()]


async def create_login_log(db: AsyncSession, data: LoginLogCreate) -> LoginLogResponse:
    """
    -- [SQL] 로그인 로그 기록
    -- INSERT INTO login_logs (player_id, success, ip_address, date, created_at)
    -- VALUES (:player_id, :success, :ip, :date, NOW());
    """
    log = LoginLog(**data.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return LoginLogResponse.model_validate(log)
