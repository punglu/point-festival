"""Wagle device PIN: an optional screen lock, deliberately not a credential.

The single most important property of this module is what it *cannot* do.
There is no function that returns a PIN, and no combination of the ones here
produces one — recovery is `reset_pin`, which replaces the secret, never
retrieval. A FamilyAdmin has no path in at all: every function is keyed on the
calling Account's own id, so "read a family member's PIN" is not a permission
that was denied, it is an operation that does not exist.

What it must never do, each of which would be a plausible-looking mistake:

- **Log the Account out.** Failing the PIN locks a screen on one device. The
  Account Session is untouched, so Markpoint, the Family screens and Push all
  keep working. Wiring PIN failure to session revocation would turn a UI lock
  into a denial-of-service on the whole platform.
- **Block Push.** A locked device keeps receiving notifications and unread
  counts; only the conversation *content* is gated. That is the approved
  behaviour, not an oversight.
- **Reuse the legacy player PIN.** `auth.models.pin_hash` authenticates a
  legacy MarkPoint player. Sharing it would make a screen lock into a login
  credential and couple a Target feature to a retiring one.
- **Be Family-scoped.** One personal PIN per device spans every Family that
  Account can reach. A per-Family PIN would leak a personal device setting into
  family-visible state.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domains.family import auth_service
from app.domains.wagle.realtime_models import WagleDevicePin

# Reused from the Account credential path on purpose: bcrypt, with a real work
# factor and a constant-time comparison inside `checkpw`. A hand-rolled digest
# or a `==` on hex would make a 6-digit secret trivially brute-forceable and
# timing-observable.
_hash_pin = auth_service.hash_password
_verify_pin = auth_service.verify_password


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_device_id(device_id: str | None) -> str:
    value = (device_id or "").strip()
    if not value or len(value) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="기기 식별자가 올바르지 않습니다")
    return value


def validate_pin_format(raw_pin: str) -> None:
    """Digits only, at the configured length.

    Length lives in config because it is an undecided UX value; this function
    enforces whatever that value is rather than hard-coding a policy.
    """
    expected = settings.WAGLE_PIN_LENGTH
    if not isinstance(raw_pin, str) or len(raw_pin) != expected or not raw_pin.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PIN은 숫자 {expected}자리여야 합니다",
        )


async def _load(db: AsyncSession, account_id: int, device_id: str) -> WagleDevicePin | None:
    return (
        await db.execute(
            select(WagleDevicePin).where(
                WagleDevicePin.account_id == account_id,
                WagleDevicePin.device_id == device_id,
            )
        )
    ).scalars().first()


def _is_locked(row: WagleDevicePin) -> bool:
    return row.locked_until is not None and row.locked_until > _now()


def status_payload(row: WagleDevicePin | None) -> dict:
    """What the client is allowed to know.

    Never the hash, never the raw attempt counter. `remaining_attempts` is
    derived and clamped: it is genuinely useful to a legitimate user and tells
    an attacker nothing they could not learn by trying.
    """
    if row is None or row.disabled_at is not None:
        return {
            "configured": False,
            "locked": False,
            "locked_until": None,
            "remaining_attempts": None,
            "pin_version": None,
        }
    locked = _is_locked(row)
    remaining = max(0, settings.WAGLE_PIN_MAX_ATTEMPTS - int(row.failed_attempt_count))
    return {
        "configured": True,
        "locked": locked,
        "locked_until": row.locked_until.astimezone(timezone.utc).isoformat() if locked else None,
        "remaining_attempts": 0 if locked else remaining,
        "pin_version": int(row.pin_version),
    }


async def get_status(db: AsyncSession, account_id: int, device_id: str) -> dict:
    return status_payload(await _load(db, account_id, _normalize_device_id(device_id)))


async def set_pin(db: AsyncSession, account_id: int, device_id: str, raw_pin: str) -> dict:
    """Create or replace this device's PIN.

    Replacing clears the failure state and bumps `pin_version` — a client
    holding an "unlocked" flag from the previous PIN must be forced to
    re-verify rather than inherit the unlock.
    """
    device = _normalize_device_id(device_id)
    validate_pin_format(raw_pin)
    row = await _load(db, account_id, device)
    if row is None:
        row = WagleDevicePin(account_id=account_id, device_id=device, pin_hash=_hash_pin(raw_pin))
        db.add(row)
    else:
        row.pin_hash = _hash_pin(raw_pin)
        row.pin_version = int(row.pin_version) + 1
        row.disabled_at = None
    row.failed_attempt_count = 0
    row.locked_until = None
    await db.commit()
    await db.refresh(row)
    return status_payload(row)


async def verify_pin(db: AsyncSession, account_id: int, device_id: str, raw_pin: str) -> dict:
    """Check the PIN for this device.

    A wrong PIN increments this device's own counter and, at the limit, applies
    a temporary lock. It does not touch the Account, the Session, or any other
    device of the same Account.
    """
    device = _normalize_device_id(device_id)
    row = await _load(db, account_id, device)
    if row is None or row.disabled_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="설정된 PIN이 없습니다")

    if _is_locked(row):
        # Do not evaluate the PIN at all while locked: doing so would let an
        # attacker keep testing candidates during the lockout and learn the
        # answer from the timing difference.
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="잠시 후 다시 시도해주세요",
        )

    if not isinstance(raw_pin, str) or not _verify_pin(raw_pin, row.pin_hash):
        row.failed_attempt_count = int(row.failed_attempt_count) + 1
        if row.failed_attempt_count >= settings.WAGLE_PIN_MAX_ATTEMPTS:
            row.locked_until = _now() + timedelta(seconds=settings.WAGLE_PIN_LOCK_DURATION_SECONDS)
        await db.commit()
        await db.refresh(row)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN이 올바르지 않습니다",
            headers={"X-Wagle-Pin-Remaining": str(status_payload(row)["remaining_attempts"])},
        )

    row.failed_attempt_count = 0
    row.locked_until = None
    row.last_unlocked_at = _now()
    await db.commit()
    await db.refresh(row)
    return {"unlocked": True, **status_payload(row)}


async def reset_pin(db: AsyncSession, account_id: int, device_id: str, new_pin: str) -> dict:
    """Recovery path: set a new PIN, never reveal the old one.

    Authority comes from the live Account Session the caller already holds —
    the same thing that proves they own the device's Account. There is
    deliberately no "verify the old PIN first" step: the old PIN being
    forgotten or locked out is the entire reason this endpoint exists.
    """
    device = _normalize_device_id(device_id)
    validate_pin_format(new_pin)
    row = await _load(db, account_id, device)
    if row is None:
        return await set_pin(db, account_id, device, new_pin)
    row.pin_hash = _hash_pin(new_pin)
    row.pin_version = int(row.pin_version) + 1
    row.failed_attempt_count = 0
    row.locked_until = None
    row.disabled_at = None
    row.last_reset_at = _now()
    await db.commit()
    await db.refresh(row)
    return status_payload(row)


async def disable_pin(db: AsyncSession, account_id: int, device_id: str, raw_pin: str) -> dict:
    """Turn the lock off for this device. Requires the current PIN.

    Unlike reset, this one *does* demand the current PIN: removing a lock is
    the operation an opportunist with brief physical access would want, and the
    legitimate "I forgot it" case is already served by reset.
    """
    device = _normalize_device_id(device_id)
    await verify_pin(db, account_id, device, raw_pin)
    row = await _load(db, account_id, device)
    if row is not None:
        row.disabled_at = _now()
        row.failed_attempt_count = 0
        row.locked_until = None
        await db.commit()
    return status_payload(None)
