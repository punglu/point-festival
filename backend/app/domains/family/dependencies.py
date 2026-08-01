"""Account-native authorization dependencies (Wave 1, D3/D7).

This is the Target replacement for the legacy `get_current_user` ->
`LegacyIdentityMapping` -> Account chain. Nothing here reads a legacy
`player_auth`/`admin_auth` row or `legacy_identity_mappings`: an Account is
resolved from its own Session, and family access is revalidated per request
from the server's own Membership/Role data (D7).

`ActiveFamilyContext` intentionally has no representation here. The family a
request acts on comes from the route path, and is authorized on its own merits
every time — a client-selected "current family" is never an input to any
decision in this module.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domains.family import auth_service, service as family_service
from app.domains.family.models import Account, FamilyMembership

account_bearer = HTTPBearer(auto_error=False)


async def get_current_account(
    credentials: HTTPAuthorizationCredentials | None = Depends(account_bearer),
    db: AsyncSession = Depends(get_db),
) -> Account:
    """Resolve the calling Account from an Account-native access token.

    Two independent checks: the token must be a valid Account token, and its
    Session must still be live. A revoked Session therefore stops working
    immediately rather than lingering until the access token expires.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = auth_service.decode_access_token(credentials.credentials)

    session_id = payload.get("sid")
    if session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="세션 정보가 없는 토큰입니다")
    session_row = await auth_service.load_active_session(db, int(session_id))

    try:
        account_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다")
    if session_row.account_id != account_id:
        # Token and session disagree about who is calling.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 세션입니다")

    account = await db.get(Account, account_id)
    if account is None or account.status != "active" or account.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="사용할 수 없는 계정입니다")
    return account


async def get_current_session_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(account_bearer),
) -> int:
    """The calling Session's id, for logout of exactly this session."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다")
    payload = auth_service.decode_access_token(credentials.credentials)
    session_id = payload.get("sid")
    if session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="세션 정보가 없는 토큰입니다")
    return int(session_id)


async def get_family_membership(
    family_id: int = Path(..., description="FamilyGroup id from the route path"),
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> FamilyMembership:
    """Revalidate that this Account holds an ACTIVE Membership in this family.

    The `familyId` comes from the path and is never trusted on its own; this
    raises 403 when the Account has no active membership in it, which is also
    what a cross-family attempt produces.
    """
    return await family_service.get_active_membership(db, account.id, family_id)


def require_family_permission(permission: str):
    """Dependency factory: require one permission code within the path family.

    Usage keeps the router thin — the route declares which permission it needs
    and the check itself stays in the service layer.
    """

    async def _dependency(
        family_id: int = Path(...),
        account: Account = Depends(get_current_account),
        db: AsyncSession = Depends(get_db),
    ) -> tuple[Account, FamilyMembership]:
        membership = await family_service.get_active_membership(db, account.id, family_id)
        granted = await family_service.effective_permissions(db, membership)
        if permission not in granted:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다")
        return account, membership

    return _dependency
