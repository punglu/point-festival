"""Self-service Account notification preferences. No permission beyond
authentication -- same self-service shape as `PATCH /api/me`."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from .models import AccountNotificationPreference
from .schemas import DEFAULTS


async def get_preferences(db: AsyncSession, account_id: int) -> dict[str, bool]:
    rows = (
        await db.execute(select(AccountNotificationPreference).where(AccountNotificationPreference.account_id == account_id))
    ).scalars()
    stored = {row.pref_key: row.enabled for row in rows}
    return {**DEFAULTS, **stored}


async def set_preferences(db: AsyncSession, account_id: int, entries: dict[str, bool]) -> dict[str, bool]:
    for key, enabled in entries.items():
        stmt = pg_insert(AccountNotificationPreference).values(account_id=account_id, pref_key=key, enabled=enabled)
        stmt = stmt.on_conflict_do_update(
            index_elements=[AccountNotificationPreference.account_id, AccountNotificationPreference.pref_key],
            set_={"enabled": stmt.excluded.enabled},
        )
        await db.execute(stmt)
    await db.commit()
    return await get_preferences(db, account_id)
