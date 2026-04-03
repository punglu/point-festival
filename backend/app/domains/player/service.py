"""Player 도메인 비즈니스 로직"""
import time

import bcrypt
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.daily_point.models import DailyPoint
from app.domains.player.models import Player
from app.domains.auth.models import PlayerAuth
from app.domains.player.schema import PlayerCreate, PlayerListItem, PlayerLockRequest, PlayerUpdate, PlayerUpdateAdmin


async def get_player_list(db: AsyncSession) -> list[PlayerListItem]:
    """플레이어 목록 조회 (role='admin' 제외 + 잠금 상태 + 사진 + 총 포인트 포함)

    -- [SQL] 플레이어 목록 + 잠금 상태 + 총 포인트 조회 (admin 제외)
    -- WITH points AS (
    --   SELECT player_id, COALESCE(SUM(balance), 0) AS total_points
    --   FROM daily_points WHERE deleted_at IS NULL GROUP BY player_id
    -- )
    -- SELECT p.id, p.name, p.role, p.photo, p.last_login,
    --        pa.lock_until, COALESCE(pts.total_points, 0) AS total_points
    -- FROM players p
    -- LEFT JOIN player_auth pa ON pa.player_id = p.id
    -- LEFT JOIN points pts ON pts.player_id = p.id
    -- WHERE p.deleted_at IS NULL AND p.role != 'admin'
    -- ORDER BY p.id;
    """
    points_subq = (
        select(
            DailyPoint.player_id,
            func.coalesce(func.sum(DailyPoint.balance), 0).label("total_points"),
        )
        .where(DailyPoint.deleted_at.is_(None))
        .group_by(DailyPoint.player_id)
        .subquery()
    )

    result = await db.execute(
        select(Player, PlayerAuth.lock_until, points_subq.c.total_points)
        .outerjoin(PlayerAuth, PlayerAuth.player_id == Player.id)
        .outerjoin(points_subq, points_subq.c.player_id == Player.id)
        .where(Player.deleted_at.is_(None), Player.role != "admin")
        .order_by(Player.id)
    )
    rows = result.all()
    now_ms = int(time.time() * 1000)

    return [
        PlayerListItem(
            id=player.id,
            name=player.name,
            role=player.role,
            photo=player.photo,
            last_login=player.last_login,
            is_locked=player.is_locked or bool(lock_until and now_ms < lock_until),
            total_points=int(total_points or 0),
        )
        for player, lock_until, total_points in rows
    ]


async def get_player_by_id(db: AsyncSession, player_id: int) -> PlayerListItem:
    """
    -- [SQL] SELECT * FROM players WHERE id = :id AND deleted_at IS NULL;
    """
    result = await db.execute(
        select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")
    return PlayerListItem.model_validate(player)


async def create_player(db: AsyncSession, data: PlayerCreate) -> PlayerListItem:
    """플레이어 등록 (중복 이름 409, player_auth PIN 함께 생성)

    -- [SQL] 플레이어 생성
    -- SELECT id FROM players WHERE name = :name AND deleted_at IS NULL;
    -- INSERT INTO players (name, role) VALUES (:name, :role);
    -- INSERT INTO player_auth (player_id, pin_hash) VALUES (:pid, :hash);
    """
    existing = await db.execute(
        select(Player).where(Player.name == data.name, Player.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"'{data.name}' 이미 존재합니다")

    player = Player(name=data.name, role=data.role)
    db.add(player)
    await db.flush()

    pin_hash = bcrypt.hashpw(data.pin.encode(), bcrypt.gensalt()).decode()
    db.add(PlayerAuth(player_id=player.id, pin_hash=pin_hash))

    await db.commit()
    await db.refresh(player)
    return PlayerListItem.model_validate(player)


async def soft_delete_player(db: AsyncSession, player_id: int) -> None:
    """플레이어 소프트 삭제 (admin 계정 삭제 금지)

    -- [SQL] 소프트 삭제
    -- SELECT * FROM players WHERE id = :id AND deleted_at IS NULL;
    -- UPDATE players SET deleted_at = NOW() WHERE id = :id;
    """
    stmt = select(Player).where(Player.id == player_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="플레이어를 찾을 수 없습니다")
    if player.role == "admin":
        raise HTTPException(status_code=403, detail="관리자 계정은 삭제할 수 없습니다")
    player.deleted_at = func.now()
    await db.commit()


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


async def change_player_pin(db: AsyncSession, player_id: int, pin: str) -> None:
    """Admin 전용 — 플레이어 PIN 변경 (bcrypt 해시)

    -- [SQL] 플레이어 인증 정보 조회 후 PIN 해시 업데이트
    -- SELECT * FROM player_auth WHERE player_id = :player_id AND deleted_at IS NULL;
    -- UPDATE player_auth SET pin_hash = :new_hash WHERE id = :id;
    """
    stmt = select(PlayerAuth).where(PlayerAuth.player_id == player_id, PlayerAuth.deleted_at.is_(None))
    result = await db.execute(stmt)
    auth = result.scalar_one_or_none()
    if not auth:
        raise HTTPException(status_code=404, detail="플레이어 인증 정보를 찾을 수 없습니다")
    auth.pin_hash = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    await db.commit()


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
