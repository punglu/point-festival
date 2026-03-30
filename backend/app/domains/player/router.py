from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.player.schema import PlayerListItem, PlayerUpdate
from app.domains.player.service import get_player_list, update_player

router = APIRouter(prefix="/api/players", tags=["Player"])


@router.get("", response_model=list[PlayerListItem])
async def list_players(db: AsyncSession = Depends(get_db)):
    """플레이어 목록 조회 (Auth 페이지 PlayerSelector용)"""
    return await get_player_list(db)


@router.patch("/{player_id}", response_model=PlayerListItem)
async def edit_player(player_id: int, data: PlayerUpdate, db: AsyncSession = Depends(get_db)):
    """플레이어 정보 수정 (상태 메시지)"""
    return await update_player(db, player_id, data)
