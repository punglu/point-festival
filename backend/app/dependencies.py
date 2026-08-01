"""Current-model JWT authentication and ownership guards for legacy routes."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    JWT 토큰에서 사용자 정보 추출.

    허용 역할: player / admin (레거시) + account (Target, Wave 1 D2/D3).

    MONGLE-W6-TARGET-UI-MULTIFAMILY-JOURNEY-001: `account`가 추가된 이유는
    Target 자격증명이 Target 라우트에 닿지 못했기 때문이다. `/api/account-context`
    와 Wagle 15개 라우트가 이 의존성을 쓰는데 Account Session을 401로 거부해,
    Wave 1~3에서 완성된 기능을 브라우저에서 전혀 열 수 없었다. 역할 집합에
    한 값을 더하는 것이 최소 수정이며, 어떤 라우터도 바뀌지 않는다.

    Account 토큰의 Session 유효성은 `resolve_current_account`가 DB에서 재확인한다
    — 여기서는 서명과 역할만 본다.
    반환: {"sub": "1", "name": "유빈", "role": "player", ...}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("role") not in {"player", "admin", "account"}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰 역할입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """관리자 권한 필수 (role != 'admin'이면 403)"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return user


async def get_current_player(user: dict = Depends(get_current_user)) -> dict:
    """Require a player token and normalize the current player ID once."""
    if user.get("role") != "player":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="플레이어 권한이 필요합니다")
    try:
        return {**user, "player_id": int(user["sub"])}
    except (ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다")


def require_self_player_id(user: dict, requested_player_id: Optional[int]) -> int:
    """Reject caller-controlled cross-player access in the current schema model."""
    current_player_id = user["player_id"]
    if requested_player_id is not None and requested_player_id != current_player_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="다른 사용자의 데이터에 접근할 수 없습니다")
    return current_player_id
