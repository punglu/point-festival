from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.notification.models import Notification
from app.domains.notification.schema import NotificationCreate, NotificationResponse


async def get_unread_notifications(db: AsyncSession) -> list[NotificationResponse]:
    """
    -- [SQL] 읽지 않은 알림 목록 조회
    -- SELECT * FROM notifications
    -- WHERE is_read = FALSE AND deleted_at IS NULL
    -- ORDER BY created_at DESC;
    """
    stmt = (
        select(Notification)
        .where(Notification.is_read.is_(False), Notification.deleted_at.is_(None))
        .order_by(Notification.created_at.desc())
    )
    result = await db.execute(stmt)
    return [NotificationResponse.model_validate(r) for r in result.scalars().all()]


async def get_all_notifications(db: AsyncSession) -> list[NotificationResponse]:
    """
    -- [SQL] 전체 알림 목록 조회 (읽음 포함)
    -- SELECT * FROM notifications
    -- WHERE deleted_at IS NULL
    -- ORDER BY created_at DESC;
    """
    stmt = (
        select(Notification)
        .where(Notification.deleted_at.is_(None))
        .order_by(Notification.created_at.desc())
    )
    result = await db.execute(stmt)
    return [NotificationResponse.model_validate(r) for r in result.scalars().all()]


async def emit_notification(
    db: AsyncSession,
    type: str,
    player_id: Optional[int],
    title: str,
    body: Optional[str] = None,
) -> None:
    """
    -- [SQL] 알림 생성 (이벤트 트리거용 — commit 없음, 호출자가 commit)
    -- INSERT INTO notifications (type, player_id, title, body, is_read, created_at)
    -- VALUES (:type, :player_id, :title, :body, FALSE, NOW());
    """
    notif = Notification(type=type, player_id=player_id, title=title, body=body, is_read=False)
    db.add(notif)


async def create_notification(db: AsyncSession, data: NotificationCreate) -> NotificationResponse:
    """
    -- [SQL] 알림 생성
    -- INSERT INTO notifications (type, player_id, title, body, created_at) VALUES (..., NOW());
    """
    notif = Notification(**data.model_dump())
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return NotificationResponse.model_validate(notif)


async def mark_as_read(db: AsyncSession, notification_id: int) -> None:
    """
    -- [SQL] 알림 읽음 처리
    -- UPDATE notifications SET is_read = TRUE WHERE id = :id AND deleted_at IS NULL;
    """
    stmt = select(Notification).where(
        Notification.id == notification_id, Notification.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
    notif.is_read = True
    await db.commit()


async def mark_all_as_read(db: AsyncSession) -> int:
    """
    -- [SQL] 전체 알림 읽음 처리
    -- UPDATE notifications SET is_read = TRUE WHERE is_read = FALSE AND deleted_at IS NULL;
    """
    stmt = (
        update(Notification)
        .where(Notification.is_read.is_(False), Notification.deleted_at.is_(None))
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
