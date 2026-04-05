from datetime import datetime, timezone
from sqlalchemy import select, update as sql_update, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.chat.models import ChatMessage
from app.domains.chat.schema import ChatMessageCreate, ChatMessageResponse, ChatPartner
from app.domains.player.models import Player


async def get_chat_partners(db: AsyncSession, my_id: int) -> list[ChatPartner]:
    """
    -- [SQL] 대화 상대 목록 + 마지막 메시지 + 안 읽은 수
    -- SELECT p.id, p.name, p.photo FROM players p WHERE p.id != :me AND p.deleted_at IS NULL;
    -- 각 상대별:
    --   마지막 메시지: SELECT message, created_at FROM chat_messages WHERE ... ORDER BY created_at DESC LIMIT 1;
    --   안읽은 수: SELECT COUNT(*) FROM chat_messages WHERE sender_id=:pid AND receiver_id=:me AND is_read=FALSE;
    """
    stmt = select(Player).where(Player.id != my_id, Player.deleted_at.is_(None))
    result = await db.execute(stmt)
    players = result.scalars().all()

    partners = []
    for p in players:
        last_msg_stmt = (
            select(ChatMessage).where(
                or_(
                    and_(ChatMessage.sender_id == my_id, ChatMessage.receiver_id == p.id),
                    and_(ChatMessage.sender_id == p.id, ChatMessage.receiver_id == my_id),
                ),
                ChatMessage.deleted_at.is_(None),
            ).order_by(desc(ChatMessage.created_at)).limit(1)
        )
        last_result = await db.execute(last_msg_stmt)
        last_msg = last_result.scalar_one_or_none()

        unread_stmt = select(func.count(ChatMessage.id)).where(
            ChatMessage.sender_id == p.id,
            ChatMessage.receiver_id == my_id,
            ChatMessage.is_read.is_(False),
            ChatMessage.deleted_at.is_(None),
        )
        unread_result = await db.execute(unread_stmt)
        unread = unread_result.scalar() or 0

        partners.append(ChatPartner(
            player_id=p.id, name=p.name, photo=p.photo,
            last_message=last_msg.message if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None,
            unread_count=unread,
        ))

    partners.sort(
        key=lambda x: x.last_message_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return partners


async def get_chat_history(
    db: AsyncSession, my_id: int, partner_id: int,
    limit: int = 50, before_id: int | None = None,
) -> list[ChatMessageResponse]:
    """
    -- [SQL] 두 사용자 간 대화 히스토리 (최신순, 페이지네이션)
    -- SELECT cm.*, p.name, p.photo FROM chat_messages cm JOIN players p ON cm.sender_id = p.id
    -- WHERE ((sender_id=:me AND receiver_id=:partner) OR (sender_id=:partner AND receiver_id=:me))
    --   AND cm.deleted_at IS NULL [AND cm.id < :before_id] ORDER BY cm.created_at DESC LIMIT :limit;
    """
    stmt = (
        select(ChatMessage, Player.name, Player.photo)
        .join(Player, ChatMessage.sender_id == Player.id)
        .where(
            or_(
                and_(ChatMessage.sender_id == my_id, ChatMessage.receiver_id == partner_id),
                and_(ChatMessage.sender_id == partner_id, ChatMessage.receiver_id == my_id),
            ),
            ChatMessage.deleted_at.is_(None),
        )
    )
    if before_id:
        stmt = stmt.where(ChatMessage.id < before_id)
    stmt = stmt.order_by(desc(ChatMessage.created_at)).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    return [
        ChatMessageResponse(
            id=msg.id, sender_id=msg.sender_id, receiver_id=msg.receiver_id,
            message=msg.message, is_read=msg.is_read, created_at=msg.created_at,
            sender_name=name, sender_photo=photo,
        )
        for msg, name, photo in rows
    ]


async def send_message(
    db: AsyncSession, sender_id: int, data: ChatMessageCreate,
) -> ChatMessageResponse:
    """
    -- [SQL] 메시지 전송
    -- INSERT INTO chat_messages (sender_id, receiver_id, message) VALUES (:sid, :rid, :msg);
    """
    msg = ChatMessage(sender_id=sender_id, receiver_id=data.receiver_id, message=data.message)
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    sender = await db.get(Player, sender_id)
    return ChatMessageResponse(
        id=msg.id, sender_id=msg.sender_id, receiver_id=msg.receiver_id,
        message=msg.message, is_read=msg.is_read, created_at=msg.created_at,
        sender_name=sender.name if sender else None,
        sender_photo=sender.photo if sender else None,
    )


async def mark_as_read(db: AsyncSession, my_id: int, partner_id: int) -> int:
    """
    -- [SQL] 상대방이 보낸 메시지 읽음 처리
    -- UPDATE chat_messages SET is_read = TRUE
    -- WHERE sender_id = :partner AND receiver_id = :me AND is_read = FALSE AND deleted_at IS NULL;
    """
    stmt = (
        sql_update(ChatMessage).where(
            ChatMessage.sender_id == partner_id,
            ChatMessage.receiver_id == my_id,
            ChatMessage.is_read.is_(False),
            ChatMessage.deleted_at.is_(None),
        ).values(is_read=True)
    )
    result = await db.execute(stmt)
    return result.rowcount


async def get_total_unread(db: AsyncSession, my_id: int) -> int:
    """
    -- [SQL] 내 전체 안 읽은 메시지 수
    -- SELECT COUNT(*) FROM chat_messages WHERE receiver_id = :me AND is_read = FALSE AND deleted_at IS NULL;
    """
    stmt = select(func.count(ChatMessage.id)).where(
        ChatMessage.receiver_id == my_id,
        ChatMessage.is_read.is_(False),
        ChatMessage.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar() or 0
