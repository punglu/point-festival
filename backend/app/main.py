from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.domains.auth.router import router as auth_router
from app.domains.player.router import router as player_router
from app.domains.mission.router import router as mission_router
from app.domains.cheer.router import router as cheer_router
from app.domains.feedback.router import router as feedback_router
from app.domains.deduction.router import router as deduction_router
from app.domains.daily_point.router import router as daily_point_router
from app.domains.notification.router import router as notification_router
from app.domains.config.router import router as config_router
from app.domains.login_log.router import router as login_log_router
from app.domains.admin.router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 마감 경과 미션 자동 실패 처리
    try:
        from app.database import AsyncSessionLocal
        from app.domains.mission.service import expire_overdue_missions
        async with AsyncSessionLocal() as db:
            count = await expire_overdue_missions(db)
            if count > 0:
                print(f"[startup] 마감 경과 미션 {count}건 실패 처리")
    except Exception as e:
        print(f"[startup] 미션 만료 처리 실패: {e}")
    yield


app = FastAPI(
    title="MC Point Festival API",
    version="1.0.0",
    description="마인크래프트 포인트 잔치 백엔드 API",
    lifespan=lifespan,
)

# CORS (개발 환경 — 프로덕션은 nginx 프록시로 대체)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(player_router)
app.include_router(mission_router)
app.include_router(cheer_router)
app.include_router(feedback_router)
app.include_router(deduction_router)
app.include_router(daily_point_router)
app.include_router(notification_router)
app.include_router(config_router)
app.include_router(login_log_router)
app.include_router(admin_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "mc-point-festival"}
