"""RBAC 의존성 함수 — FastAPI Depends로 주입되는 인증/인가 미들웨어"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.domains.auth.models import AdminAuth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """JWT 디코딩 → player_id + is_admin 반환 (Player 전용)"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        role = payload.get("role")
        if role != "player":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Player token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {
            "player_id": int(payload["sub"]),
            "is_admin": payload.get("is_admin", False),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminAuth:
    """JWT 디코딩 → admin_auth 조회 (Admin 전용).

    Legacy admin 토큰(`role == "admin"`)은 그대로 처리한다. Account-native
    토큰(`role == "account"`)은 기존 `LegacyIdentityMapping` 브릿지를 통해
    실제 admin_auth 신원과 연결된 경우에만 그 admin_auth 행을 반환한다 --
    DEFECT-001 (MONGLE-W7-4-ADMIN-ACCOUNT-AUTH-ACCESS-CONTRACT-
    REMEDIATION-001). `/api/admin/*`(이 모듈이 실제로 게이트하는 라우터)가
    지금까지 `app.dependencies.require_admin`과는 별도로 동일한 legacy-only
    검사를 중복 구현하고 있었으므로, 두 곳 모두 같은 방식으로 넓힌다. 새
    권한 체계나 새 role은 도입하지 않는다.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role")
    if role == "admin":
        try:
            admin_id = int(payload["sub"])
        except (ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        admin = await db.get(AdminAuth, admin_id)
        if not admin or admin.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
        return admin

    if role == "account":
        from app.domains.family.service import resolve_linked_admin_auth

        linked_admin = await resolve_linked_admin_auth(db, payload)
        if linked_admin is not None:
            return linked_admin

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin token required",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_chat_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Player 또는 Admin 토큰 모두 허용 — chat 전용 의존성
    player token: sub=player_id
    admin token:  player_id claim 사용
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        role = payload.get("role")
        if role == "player":
            return {"player_id": int(payload["sub"])}
        elif role == "admin":
            pid = payload.get("player_id")
            if not pid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin 계정에 player_id가 없습니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return {"player_id": int(pid)}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰 역할입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Admin 권한 검증 — is_admin=False이면 403 (Player PIN 기반 레거시)"""
    if not current_user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
