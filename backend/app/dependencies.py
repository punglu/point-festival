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
    JWT 토큰에서 사용자 정보 추출 (역할 제한 없음 — player/admin 모두 허용).
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
        if payload.get("role") not in {"player", "admin"}:
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
