from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.domains.auth.schema import LoginRequest, LoginResponse, AdminLoginRequest, AdminLoginResponse
from app.domains.auth.service import authenticate_player, authenticate_admin, logout as auth_logout, handle_logout

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """플레이어 PIN 로그인"""
    return await authenticate_player(db, req)


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """관리자 ID/PW 로그인"""
    return await authenticate_admin(
        db=db, username=request.username, password=request.password
    )


@router.post("/logout")
async def logout(
    _: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """로그아웃 (클라이언트 측 토큰 삭제)"""
    await auth_logout(db)
    return await handle_logout()
