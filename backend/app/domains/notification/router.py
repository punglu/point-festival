from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_player, require_admin
from app.domains.notification.schema import NotificationCreate, NotificationResponse
from app.domains.notification.service import (
    get_unread_notifications, create_notification, mark_as_read, mark_all_as_read,
)

router = APIRouter(prefix="/api/notifications", tags=["Notification"])


@router.get("/", response_model=list[NotificationResponse])
async def list_unread(
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """읽지 않은 알림 목록"""
    return await get_unread_notifications(db, user["player_id"])


@router.post("/", response_model=NotificationResponse, status_code=201)
async def add_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """알림 생성"""
    return await create_notification(db, data)


@router.patch("/{notification_id}/read", status_code=204)
async def read_one(
    notification_id: int,
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """알림 개별 읽음 처리"""
    await mark_as_read(db, notification_id, user["player_id"])


@router.patch("/read-all", status_code=204)
async def read_all(
    user: dict = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    """전체 알림 읽음 처리"""
    await mark_all_as_read(db, user["player_id"])
