"""Player 도메인 비즈니스 로직"""
import time

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.player.models import Player
from app.domains.auth.models import PlayerAuth
from app.domains.player.schema import PlayerListItem, PlayerLockRequest, PlayerUpdate, PlayerUpdateAdmin


async def get_player_list(db: AsyncSession) -> list[PlayerListItem]:
    """플레이어 목록 조회 (잠금 상태 포함)

    -- [SQL] 플레이어 목록 + 잠금 상태 조회
    -- SELECT p.id, p.name, p.role, p.last_login,
    --        pa.lock_until
    -- FROM players p
    -- LEFT JOIN player_auth pa ON pa.player_id = p.id
    -- WHERE p.deleted_at IS NULL
    -- ORDER BY p.id;
    """
    result = await db.execute(
        select(Player, PlayerAuth.lock_until)
        .outerjoin(PlayerAuth, PlayerAuth.player_id == Player.id)
        .where(Player.deleted_at.is_(None))
        .order_by(Player.id)
    )
    rows = result.all()
    now_ms = int(time.time() * 1000)

    return [
        PlayerListItem(
            id=player.id,
            name=player.name,
            role=player.role,
            last_login=player.last_login,
            is_locked=player.is_locked or bool(lock_until and now_ms < lock_until),
        )
        for player, lock_until in rows
    ]


async def update_player_admin(db: AsyncSession, player_id: int, data: PlayerUpdateAdmin) -> PlayerListItem:
    """Admin 전용 — 플레이어 정보 수정 (이름, 사진, 상태 메시지)

    -- [SQL] Admin 플레이어 정보 수정
    -- UPDATE players SET name = :name, photo = :photo, status_msg = :status_msg, updated_at = NOW()
    -- WHERE id = :player_id AND deleted_at IS NULL;
    """
    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    await db.commit()
    await db.refresh(player)
    return PlayerListItem.model_validate(player)


async def lock_player(db: AsyncSession, player_id: int, data: PlayerLockRequest) -> PlayerListItem:
    """Admin 전용 — 플레이어 잠금/해제

    -- [SQL] 플레이어 잠금 상태 변경
    -- UPDATE players SET is_locked = :is_locked, updated_at = NOW()
    -- WHERE id = :player_id AND deleted_at IS NULL;
    """
    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")
    player.is_locked = data.is_locked
    await db.commit()
    await db.refresh(player)
    return PlayerListItem.model_validate(player)


async def update_player(db: AsyncSession, player_id: int, data: PlayerUpdate) -> PlayerListItem:
    """플레이어 정보 수정

    -- [SQL] 플레이어 정보 수정
    -- UPDATE players SET status_msg = :status_msg, updated_at = NOW()
    -- WHERE id = :player_id AND deleted_at IS NULL;
    """
    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    await db.commit()
    await db.refresh(player)
    return PlayerListItem.model_validate(player)
