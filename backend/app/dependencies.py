"""공통 의존성 — JWT role 기반 인증/인가 (mission 등 플레이어/관리자 공용 엔드포인트용)"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    JWT 토큰에서 사용자 정보 추출 (역할 제한 없음 — player/admin 모두 허용).
    반환: {"sub": "1", "name": "유빈", "role": "player", ...}
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
        )


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """관리자 권한 필수 (role != 'admin'이면 403)"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return user
