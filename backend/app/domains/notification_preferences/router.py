from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.family.dependencies import get_current_account
from app.domains.family.models import Account
from . import service
from .schemas import PreferenceOut, PreferencesReplace

router = APIRouter(tags=["notification-preferences"])


def _out(prefs: dict[str, bool]) -> list[PreferenceOut]:
    return [PreferenceOut(pref_key=key, enabled=enabled) for key, enabled in prefs.items()]


@router.get("/api/me/notification-preferences", response_model=list[PreferenceOut])
async def read_preferences(account: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return _out(await service.get_preferences(db, account.id))


@router.put("/api/me/notification-preferences", response_model=list[PreferenceOut])
async def update_preferences(body: PreferencesReplace, account: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    entries = {entry.pref_key: entry.enabled for entry in body.preferences}
    return _out(await service.set_preferences(db, account.id, entries))
