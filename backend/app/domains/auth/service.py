"""Auth 도메인 비즈니스 로직
PIN 인증, 잠금 처리, JWT 발급
"""
import time
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from app.domains.auth.models import PlayerAuth, AdminAuth
from app.domains.auth.schema import LoginRequest, LoginResponse, AdminLoginResponse
from app.domains.player.models import Player
from app.config import settings
from jose import jwt




async def authenticate_player(
    db: AsyncSession,
    req: LoginRequest
) -> LoginResponse:
    """플레이어 PIN 인증 및 JWT 발급

    -- [SQL] 플레이어 인증 정보 조회
    -- SELECT pa.id, pa.player_id, pa.pin_hash, pa.login_attempts, pa.lock_until,
    --        p.name, p.role
    -- FROM player_auth pa
    -- JOIN players p ON p.id = pa.player_id
    -- WHERE pa.player_id = :player_id
    --   AND pa.deleted_at IS NULL
    --   AND p.deleted_at IS NULL;
    """
    result = await db.execute(
        select(PlayerAuth, Player.name, Player.role, Player.is_locked)
        .join(Player, Player.id == PlayerAuth.player_id)
        .where(
            PlayerAuth.player_id == req.player_id,
            PlayerAuth.deleted_at.is_(None),
            Player.deleted_at.is_(None),
        )
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 플레이어가 아닙니다."
        )

    auth: PlayerAuth = row[0]
    player_name: str = row[1]
    player_role: str = row[2]
    player_is_locked: bool = row[3]

    # Admin 잠금 상태 확인 (영구 잠금)
    if player_is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="🔒 관리자에 의해 잠긴 계정입니다.",
        )

    # 잠금 상태 확인
    now_ms = int(time.time() * 1000)
    if auth.lock_until and now_ms < auth.lock_until:
        remaining = (auth.lock_until - now_ms) // 1000
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"🔒 {remaining}초 후에 다시 시도해주세요.",
        )

    # PIN 검증
    if not bcrypt.checkpw(req.pin.encode("utf-8"), auth.pin_hash.encode("utf-8")):
        new_attempts = auth.login_attempts + 1
        await _increment_attempts(db, auth, new_attempts, now_ms)
        await _save_login_log(db, req.player_id, success=False)

        if new_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"{settings.MAX_LOGIN_ATTEMPTS}회 실패하여 {settings.LOCK_DURATION_SECONDS // 60}분간 잠금되었습니다.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"잘못된 PIN입니다. ({new_attempts}/{settings.MAX_LOGIN_ATTEMPTS})",
        )

    # 인증 성공: 시도 횟수 초기화 + 마지막 접속 갱신
    """
    -- [SQL] 로그인 성공 시 초기화
    -- UPDATE player_auth SET login_attempts = 0, lock_until = NULL
    --   WHERE player_id = :player_id;
    -- UPDATE players SET last_login = :now WHERE id = :player_id;
    """
    await db.execute(
        update(PlayerAuth)
        .where(PlayerAuth.player_id == req.player_id)
        .values(login_attempts=0, lock_until=None)
    )
    await db.execute(
        update(Player)
        .where(Player.id == req.player_id)
        .values(last_login=now_ms)
    )
    await _save_login_log(db, req.player_id, success=True)
    await db.commit()

    # JWT 발급 (role + is_admin claim 포함)
    token = await _create_jwt(req.player_id, player_name, player_role, auth.is_admin)

    return LoginResponse(
        access_token=token,
        player_id=req.player_id,
        player_name=player_name,
        player_role=player_role,
        is_admin=auth.is_admin,
    )


async def _increment_attempts(
    db: AsyncSession, auth: PlayerAuth, new_attempts: int, now_ms: int
) -> None:
    """
    -- UPDATE player_auth
    -- SET login_attempts = CASE
    --     WHEN login_attempts + 1 >= :max_attempts THEN 0
    --     ELSE login_attempts + 1
    -- END,
    -- lock_until = CASE
    --     WHEN login_attempts + 1 >= :max_attempts THEN :lock_until_ms
    --     ELSE NULL
    -- END,
    -- updated_at = NOW()
    -- WHERE player_id = :player_id
    """
    values: dict = {"login_attempts": new_attempts}
    if new_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        values["lock_until"] = now_ms + settings.LOCK_DURATION_SECONDS * 1000
        values["login_attempts"] = 0

    await db.execute(
        update(PlayerAuth).where(PlayerAuth.id == auth.id).values(**values)
    )
    await db.commit()


async def _save_login_log(db: AsyncSession, player_id: int, success: bool) -> None:
    """
    -- [SQL] 로그인 로그 기록
    -- INSERT INTO login_logs (player_id, success, date, created_at)
    -- VALUES (:player_id, :success, CURRENT_DATE, NOW());
    """
    await db.execute(
        text(
            "INSERT INTO login_logs (player_id, success, date, created_at) "
            "VALUES (:pid, :ok, CURRENT_DATE, NOW())"
        ),
        {"pid": player_id, "ok": success},
    )


async def authenticate_admin(
    db: AsyncSession,
    username: str,
    password: str,
) -> AdminLoginResponse:
    """관리자 ID/PW 인증 및 JWT 발급

    -- [SQL] 관리자 인증 정보 조회
    -- SELECT * FROM admin_auth
    -- WHERE username = :username
    --   AND deleted_at IS NULL;
    """
    result = await db.execute(
        select(AdminAuth).where(
            AdminAuth.username == username,
            AdminAuth.deleted_at.is_(None),
        )
    )
    admin = result.scalars().first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    try:
        password_matches = bcrypt.checkpw(password.encode("utf-8"), admin.password.encode("utf-8"))
    except (ValueError, TypeError):
        # bcrypt raises ValueError for a >72-byte password (RE-QA-F-ADMIN-
        # LOGIN-BCRYPT) instead of returning False -- an unauthenticated
        # caller who knows/guesses a valid admin username could otherwise
        # trigger a 500 with an oversized password. Same fail-closed pattern
        # already used by family/auth_service.py::verify_password.
        password_matches = False
    if not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    payload = {
        "sub": str(admin.id),
        "name": admin.display_name,
        "role": "admin",
        "is_admin": True,
        "player_id": admin.player_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return AdminLoginResponse(
        access_token=token,
        display_name=admin.display_name,
        player_id=admin.player_id,
    )


async def logout(db: AsyncSession) -> None:
    """로그아웃 처리 (현재 Stateless JWT — 향후 확장 지점)

    # DELETE FROM login sessions (JWT stateless — 현재 서버측 무효화 없음)
    # Phase 2에서 토큰 블랙리스트 또는 login_log 기록 추가 예정
    """
    pass


async def handle_logout() -> dict:
    """
    -- [SQL] 해당 없음 (클라이언트 측 토큰 삭제만 수행)
    -- 서버 측 세션/블랙리스트 미사용
    """
    return {"message": "로그아웃 완료"}


async def _create_jwt(player_id: int, player_name: str, role: str, is_admin: bool) -> str:
    """JWT 토큰 생성"""
    payload = {
        "sub": str(player_id),
        "name": player_name,
        "role": role,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
