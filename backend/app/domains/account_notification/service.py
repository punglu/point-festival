"""Account Notification service. Self-scoped only -- no permission beyond
authentication, same shape as `PATCH /api/me`. No producer function exists
here; a future integration point (e.g. mission-approval) creates rows,
out of this Slice's declared scope."""
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import AccountNotification


async def list_notifications(db: AsyncSession, account_id: int) -> list[AccountNotification]:
    stmt = select(AccountNotification).where(AccountNotification.account_id == account_id).order_by(AccountNotification.created_at.desc())
    return list((await db.execute(stmt)).scalars())


async def mark_read(db: AsyncSession, account_id: int, notification_id: int) -> AccountNotification:
    row = await db.get(AccountNotification, notification_id)
    if row is None or row.account_id != account_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="알림을 찾을 수 없습니다")
    if row.read_at is None:
        row.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(row)
    return row


async def mark_all_read(db: AsyncSession, account_id: int) -> int:
    result = await db.execute(
        update(AccountNotification)
        .where(AccountNotification.account_id == account_id, AccountNotification.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return result.rowcount or 0
