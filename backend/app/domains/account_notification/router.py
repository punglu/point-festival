from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_current_account
from app.domains.family.models import Account
from . import service
from .schemas import NotificationOut

router = APIRouter(tags=["account-notification"])


@router.get("/api/me/notifications", response_model=list[NotificationOut])
async def list_notifications(account: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return await service.list_notifications(db, account.id)


@router.post("/api/me/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_read(notification_id: int, account: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return await service.mark_read(db, account.id, notification_id)


@router.post("/api/me/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(account: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    await service.mark_all_read(db, account.id)
