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
from app.domains.mission_template.router import router as mission_template_router
from app.domains.chat.router import router as chat_router
from app.domains.level_tier.router import router as level_tier_router
from app.domains.family.router import router as family_router
from app.domains.wagle.router import router as wagle_router
from app.domains.wagle.realtime_router import router as wagle_realtime_router
from app.domains.markpoint_access.router import router as markpoint_access_router
from app.domains.markpoint_target.router import router as markpoint_target_router
from app.domains.family_todo.router import router as family_todo_router
from app.domains.family_rules.router import router as family_rules_router
from app.domains.notification_preferences.router import router as notification_preferences_router
from app.domains.family_schedule.router import router as family_schedule_router
from app.domains.family_album.router import router as family_album_router
from app.domains.reward_catalog.router import router as reward_catalog_router
from app.domains.account_notification.router import router as account_notification_router
from app.domains.family_activity_log.router import router as family_activity_log_router
from app.domains.family_search.router import router as family_search_router


async def _wagle_realtime_pump(stop: "asyncio.Event", port) -> None:
    """Drain Wagle delivery events from inside the web process.

    MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001, extended by
    MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001.

    The WebSocket registry is process-local, so the dispatcher runs *here* for
    this worker's own clients, and `port` is the LISTEN/NOTIFY fan-out that
    reaches the other ASGI workers. `app.workers.wagle_realtime` remains the
    standalone process for deployments that separate the two; running both is
    safe - `claim_batch` leases with `FOR UPDATE SKIP LOCKED`, and whichever
    loses the race publishes nothing while NOTIFY and the durable catch-up
    cover the clients either way.

    Failures here are swallowed on purpose: notification delivery must never be
    able to take the API process down. The message is already durable by the
    time this runs.
    """
    import asyncio as _asyncio

    from app.database import AsyncSessionLocal
    from app.domains.wagle import realtime_dispatcher

    while not stop.is_set():
        try:
            async with AsyncSessionLocal() as db:
                await realtime_dispatcher.run_once(db, port=port)
        except Exception:
            pass
        try:
            await _asyncio.wait_for(stop.wait(), timeout=1.0)
            return
        except _asyncio.TimeoutError:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

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

    # MONGLE-W3-WAGLE-MULTIWORKER-FANOUT-001: every ASGI worker holds its own
    # WebSocket registry, so an event committed on one worker must be announced
    # to the others. PostgreSQL LISTEN/NOTIFY is the approved channel - no new
    # infrastructure - and it is a wake-up signal only: the database and the
    # Outbox remain the source of truth, and the per-connection durable cursor
    # catch-up is deliberately kept as the fallback that makes NOTIFY optional.
    from app.domains.wagle.realtime import fanout as local_fanout
    from app.domains.wagle.realtime_notify import PostgresNotifyFanout, to_asyncpg_dsn

    notify_fanout = PostgresNotifyFanout(local_fanout, to_asyncpg_dsn(settings.DATABASE_URL))
    try:
        await notify_fanout.start_listener()
    except Exception as e:
        # A worker that cannot listen still serves its own clients correctly and
        # still recovers everything through the durable cursor; it just loses
        # instant cross-worker delivery. Degrade loudly, never fail startup.
        print(f"[wagle_realtime] LISTEN unavailable, falling back to cursor catch-up: {e}")

    stop = asyncio.Event()
    pump = asyncio.create_task(_wagle_realtime_pump(stop, notify_fanout))
    try:
        yield
    finally:
        stop.set()
        pump.cancel()
        await notify_fanout.stop_listener()


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
app.include_router(mission_template_router)
app.include_router(chat_router)
app.include_router(level_tier_router)
app.include_router(family_router)
app.include_router(wagle_router)
app.include_router(wagle_realtime_router)
app.include_router(markpoint_access_router)
app.include_router(markpoint_target_router)
app.include_router(family_todo_router)
app.include_router(family_rules_router)
app.include_router(notification_preferences_router)
app.include_router(family_schedule_router)
app.include_router(family_album_router)
app.include_router(reward_catalog_router)
app.include_router(account_notification_router)
app.include_router(family_activity_log_router)
app.include_router(family_search_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "mc-point-festival"}
