from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.domains.player.schema import PlayerCreate, PlayerListItem, PlayerUpdate
from app.domains.player.service import (
    create_player, get_player_by_id, get_player_list,
    soft_delete_player, update_player,
)

router = APIRouter(prefix="/api/players", tags=["Player"])


@router.get("", response_model=list[PlayerListItem])
async def list_players(db: AsyncSession = Depends(get_db)):
    """플레이어 목록 조회 (Auth 페이지 PlayerSelector용, admin 제외)"""
    return await get_player_list(db)


@router.get("/me", response_model=PlayerListItem)
async def get_me(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """현재 로그인 사용자 정보"""
    return await get_player_by_id(db, int(user["sub"]))


@router.post("", response_model=PlayerListItem, status_code=201)
async def add_player(data: PlayerCreate, db: AsyncSession = Depends(get_db)):
    """플레이어 등록 (Admin 전용)"""
    return await create_player(db, data)


@router.patch("/{player_id}", response_model=PlayerListItem)
async def edit_player(player_id: int, data: PlayerUpdate, db: AsyncSession = Depends(get_db)):
    """플레이어 정보 수정 (상태 메시지)"""
    return await update_player(db, player_id, data)


@router.delete("/{player_id}", status_code=204)
async def remove_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """플레이어 소프트 삭제 (admin 계정 삭제 불가)"""
    await soft_delete_player(db, player_id)
