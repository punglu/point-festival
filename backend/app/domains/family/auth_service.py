"""Account-native credential and Session lifecycle (Wave 1, D2/D3).

Responsibility axis: platform authentication for an `Account`. Family
membership, role and permission evaluation stay in `family/service.py`; this
module never decides family authorization by itself.

Deliberate boundaries:

- No Legacy path. Nothing here reads `player_auth`, `admin_auth` or
  `legacy_identity_mappings`. An Account authenticates because it has an
  `AccountCredential`, never because a legacy row maps to it (D8 RESET).
- Passwords exist only as bcrypt hashes; refresh tokens only as SHA-256
  hashes. No function in this module returns, logs, or stores a recoverable
  secret except the single generated initial password, which is handed back to
  its issuer exactly once and never persisted in plaintext.
- Session is Account-scoped. Nothing here takes a `family_id`, and no
  membership change revokes a Session.
"""
from __future__ import annotations

import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domains.family.models import Account, AccountCredential, AccountSession

# JWT claim marking an Account-native access token. The legacy player/admin
# tokens use role="player"/"admin"; this deliberately uses a distinct value so a
# legacy token can never satisfy an Account-native dependency, or vice versa.
ACCOUNT_TOKEN_ROLE = "account"

_PASSWORD_ALPHABET = string.ascii_letters + string.digits


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --- password and token primitives ---------------------------------------


def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        # A malformed stored hash must fail closed, never raise into the route.
        return False


def generate_initial_password() -> str:
    return "".join(secrets.choice(_PASSWORD_ALPHABET) for _ in range(settings.ACCOUNT_INITIAL_PASSWORD_LENGTH))


def normalize_username(username: str) -> str:
    """Case-insensitive, whitespace-insensitive login identifier.

    Stored normalized so the unique index enforces the same identity the login
    lookup uses; without this, `Alice` and `alice` would be two accounts.
    """
    return username.strip().lower()


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def create_access_token(account_id: int, session_id: int) -> str:
    payload = {
        "sub": str(account_id),
        "role": ACCOUNT_TOKEN_ROLE,
        "sid": session_id,
        "exp": _now() + timedelta(minutes=settings.ACCOUNT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("role") != ACCOUNT_TOKEN_ROLE:
        # A legacy player/admin token must not authenticate an Account route.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account 토큰이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def validate_password_strength(raw_password: str) -> None:
    if len(raw_password) < settings.ACCOUNT_PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"비밀번호는 최소 {settings.ACCOUNT_PASSWORD_MIN_LENGTH}자 이상이어야 합니다",
        )


# --- credential lifecycle -------------------------------------------------


async def get_active_credential_by_username(db: AsyncSession, username: str) -> Optional[AccountCredential]:
    """
    -- [Query] Resolve a login identifier to its live credential row.
    -- SELECT * FROM account_credentials
    --  WHERE username = :username AND deleted_at IS NULL;
    """
    stmt = select(AccountCredential).where(
        AccountCredential.username == normalize_username(username),
        AccountCredential.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalars().first()


async def get_credential_for_account(db: AsyncSession, account_id: int) -> Optional[AccountCredential]:
    stmt = select(AccountCredential).where(
        AccountCredential.account_id == account_id,
        AccountCredential.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalars().first()


async def create_credential(
    db: AsyncSession,
    account_id: int,
    username: str,
    raw_password: str,
    *,
    issued_by_account_id: Optional[int] = None,
    is_initial_credential: bool = False,
) -> AccountCredential:
    """Create the single live credential for an Account.

    -- [Intent] Establish Account-native login for a new Account.
    -- [Audit] issued_by_account_id records the provisioning FamilyAdmin.
    Caller owns the transaction; this only add()/flush()es so it can participate
    in the FamilyAdmin issuance unit of work atomically.
    """
    normalized = normalize_username(username)
    if not normalized:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="아이디를 입력해야 합니다")
    validate_password_strength(raw_password)

    existing = await get_active_credential_by_username(db, normalized)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 아이디입니다")
    if await get_credential_for_account(db, account_id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 자격증명이 있는 계정입니다")

    credential = AccountCredential(
        account_id=account_id,
        username=normalized,
        password_hash=hash_password(raw_password),
        status="active",
        is_initial_credential=is_initial_credential,
        is_password_change_required=is_initial_credential,
        issued_by_account_id=issued_by_account_id,
    )
    db.add(credential)
    await db.flush()
    return credential


async def _register_failed_attempt(db: AsyncSession, credential: AccountCredential) -> None:
    """
    -- [Intent] Throttle credential guessing.
    -- UPDATE account_credentials SET failed_attempt_count = ..., locked_until = ...
    """
    credential.failed_attempt_count += 1
    if credential.failed_attempt_count >= settings.ACCOUNT_MAX_LOGIN_ATTEMPTS:
        credential.locked_until = _now() + timedelta(seconds=settings.ACCOUNT_LOCK_DURATION_SECONDS)
        credential.failed_attempt_count = 0
    await db.commit()


def _assert_credential_usable(credential: AccountCredential) -> None:
    if credential.status != "active" or credential.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="사용할 수 없는 자격증명입니다")
    if credential.locked_until is not None and credential.locked_until > _now():
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="로그인 시도가 많아 잠시 잠금되었습니다")


async def change_password(
    db: AsyncSession,
    account_id: int,
    current_password: str,
    new_password: str,
) -> None:
    """Self-service password change. Revokes every existing Session (D3).

    -- [Intent] Rotate an Account's own password and invalidate prior sessions.
    """
    credential = await get_credential_for_account(db, account_id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="자격증명을 찾을 수 없습니다")
    _assert_credential_usable(credential)
    if not verify_password(current_password, credential.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="현재 비밀번호가 올바르지 않습니다")
    validate_password_strength(new_password)

    credential.password_hash = hash_password(new_password)
    credential.password_changed_at = _now()
    credential.is_password_change_required = False
    credential.is_initial_credential = False
    credential.failed_attempt_count = 0
    credential.locked_until = None
    await _revoke_all_sessions(db, account_id, reason="password_change")
    await db.commit()


# --- session lifecycle ----------------------------------------------------


async def _revoke_all_sessions(db: AsyncSession, account_id: int, *, reason: str) -> None:
    """Revoke every live Session of one Account. Caller owns the commit."""
    await db.execute(
        update(AccountSession)
        .where(AccountSession.account_id == account_id, AccountSession.revoked_at.is_(None))
        .values(revoked_at=_now(), revoked_reason=reason)
    )


async def _issue_session(
    db: AsyncSession,
    account_id: int,
    device_id: str,
    device_label: Optional[str],
    *,
    rotated_from_session_id: Optional[int] = None,
) -> tuple[AccountSession, str]:
    """Create a Session row and return it with its raw refresh token.

    The raw token is returned to the caller and never persisted; only its
    SHA-256 hash is stored.
    """
    raw_refresh = generate_refresh_token()
    session_row = AccountSession(
        account_id=account_id,
        refresh_token_hash=hash_refresh_token(raw_refresh),
        device_id=device_id,
        device_label=device_label,
        expires_at=_now() + timedelta(days=settings.ACCOUNT_REFRESH_TOKEN_EXPIRE_DAYS),
        last_seen_at=_now(),
        rotated_from_session_id=rotated_from_session_id,
    )
    db.add(session_row)
    await db.flush()
    return session_row, raw_refresh


async def login(
    db: AsyncSession,
    username: str,
    password: str,
    device_id: str,
    device_label: Optional[str] = None,
) -> dict:
    """Account-native login (D2). Issues an Account-scoped Session (D3).

    -- [Intent] Authenticate an Account by username + platform password and
    -- open a persistent Session. No legacy identity is consulted.
    """
    credential = await get_active_credential_by_username(db, username)
    if credential is None:
        # Same message and shape as a wrong password so the response cannot be
        # used to enumerate which usernames exist.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 올바르지 않습니다")
    _assert_credential_usable(credential)

    if not verify_password(password, credential.password_hash):
        await _register_failed_attempt(db, credential)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="아이디 또는 비밀번호가 올바르지 않습니다")

    account = await db.get(Account, credential.account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="사용할 수 없는 계정입니다")

    credential.failed_attempt_count = 0
    credential.locked_until = None
    credential.last_login_at = _now()

    session_row, raw_refresh = await _issue_session(db, account.id, device_id, device_label)
    await db.commit()

    return {
        "access_token": create_access_token(account.id, session_row.id),
        "refresh_token": raw_refresh,
        "account_id": account.id,
        "display_name": account.display_name,
        "is_password_change_required": credential.is_password_change_required,
    }


async def refresh_session(db: AsyncSession, raw_refresh_token: str) -> dict:
    """Rotate a refresh token (D3).

    The presented token's row is revoked and a new Session row is issued in the
    same transaction, so replaying the old token afterwards finds a revoked row
    and is rejected.
    """
    token_hash = hash_refresh_token(raw_refresh_token)
    session_row = (
        await db.execute(select(AccountSession).where(AccountSession.refresh_token_hash == token_hash))
    ).scalars().first()
    if session_row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh token입니다")
    if session_row.revoked_at is not None:
        # Replay of an already-rotated or revoked token.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이미 사용되었거나 취소된 refresh token입니다")
    if session_row.expires_at <= _now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="만료된 refresh token입니다")

    account = await db.get(Account, session_row.account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="사용할 수 없는 계정입니다")

    session_row.revoked_at = _now()
    session_row.revoked_reason = "refresh_rotation"
    new_session, new_raw_refresh = await _issue_session(
        db,
        session_row.account_id,
        session_row.device_id,
        session_row.device_label,
        rotated_from_session_id=session_row.id,
    )
    await db.commit()

    return {
        "access_token": create_access_token(account.id, new_session.id),
        "refresh_token": new_raw_refresh,
        "account_id": account.id,
    }


async def logout(db: AsyncSession, session_id: int) -> None:
    """Revoke exactly the current Session. Other devices stay signed in."""
    session_row = await db.get(AccountSession, session_id)
    if session_row is None or session_row.revoked_at is not None:
        return
    session_row.revoked_at = _now()
    session_row.revoked_reason = "logout"
    await db.commit()


async def list_sessions(db: AsyncSession, account_id: int) -> list[AccountSession]:
    stmt = (
        select(AccountSession)
        .where(AccountSession.account_id == account_id, AccountSession.revoked_at.is_(None))
        .order_by(AccountSession.issued_at.desc())
    )
    return list((await db.execute(stmt)).scalars())


async def unlink_device(db: AsyncSession, account_id: int, device_id: str) -> int:
    """Revoke every live Session for one (Account, device) pair (D3).

    -- [Intent] Device unlink. Returns how many sessions were revoked so the
    -- caller can distinguish a real unlink from a no-op.
    """
    result = await db.execute(
        update(AccountSession)
        .where(
            AccountSession.account_id == account_id,
            AccountSession.device_id == device_id,
            AccountSession.revoked_at.is_(None),
        )
        .values(revoked_at=_now(), revoked_reason="device_unlink")
    )
    await db.commit()
    return result.rowcount or 0


async def load_active_session(db: AsyncSession, session_id: int) -> AccountSession:
    """Resolve a Session id from an access token to a still-valid Session row.

    This is what makes the Session durable rather than a bare stateless JWT: a
    revoked Session is rejected even while its access token is unexpired.
    """
    session_row = await db.get(AccountSession, session_id)
    if session_row is None or session_row.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었거나 취소되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if session_row.expires_at <= _now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session_row


async def resolve_account_from_session_claim(db: AsyncSession, payload: dict) -> Account:
    """Resolve the live Account an Account-token payload names.

    Single source of truth for every entry point that accepts an Account-
    native token: the Session named by `sid` must still be live, it must agree
    with `sub` about which Account is calling, and that Account must still be
    active. Two call sites need this — `family.dependencies.get_current_account`
    (decodes the token itself) and the Account branch of
    `resolve_current_account` below (receives an already-decoded payload from
    the legacy-token-shaped `get_current_user`) — so the rule is defined here
    once instead of twice, since a divergence between two copies of a
    Session-liveness check is exactly the kind of drift a future security fix
    could apply to only one of them.
    """
    session_id = payload.get("sid")
    if session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="세션 정보가 없는 토큰입니다")
    session_row = await load_active_session(db, int(session_id))
    try:
        account_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다")
    if session_row.account_id != account_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 세션입니다")
    account = await db.get(Account, account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="사용할 수 없는 계정입니다")
    return account
