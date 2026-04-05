"""채팅 라우터 — 로그인 사용자 전용"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.auth.dependencies import get_current_chat_user
from app.domains.chat import service as chat_service
from app.domains.chat.schema import ChatMessageCreate, ChatMessageResponse, ChatPartner

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/partners", response_model=list[ChatPartner])
async def list_partners(
    user: dict = Depends(get_current_chat_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.get_chat_partners(db, user["player_id"])


@router.get("/history/{partner_id}", response_model=list[ChatMessageResponse])
async def get_history(
    partner_id: int,
    limit: int = 50,
    before_id: int | None = None,
    user: dict = Depends(get_current_chat_user),
    db: AsyncSession = Depends(get_db),
):
    await chat_service.mark_as_read(db, user["player_id"], partner_id)
    await db.commit()
    return await chat_service.get_chat_history(db, user["player_id"], partner_id, limit, before_id)


@router.post("/send", response_model=ChatMessageResponse, status_code=201)
async def send_message(
    data: ChatMessageCreate,
    user: dict = Depends(get_current_chat_user),
    db: AsyncSession = Depends(get_db),
):
    result = await chat_service.send_message(db, user["player_id"], data)
    await db.commit()
    return result


@router.get("/unread", response_model=dict)
async def get_unread(
    user: dict = Depends(get_current_chat_user),
    db: AsyncSession = Depends(get_db),
):
    count = await chat_service.get_total_unread(db, user["player_id"])
    return {"unread": count}
