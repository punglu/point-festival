from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    MAX_LOGIN_ATTEMPTS: int = 5
    LOCK_DURATION_SECONDS: int = 300

    # --- Account-native platform auth (Wave 1, D2/D3) -----------------------
    # Single source of truth for every Account credential/session parameter.
    # Do not re-declare any of these as literals inside domain code.
    ACCOUNT_PASSWORD_MIN_LENGTH: int = 8
    ACCOUNT_MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCK_DURATION_SECONDS: int = 300
    ACCOUNT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCOUNT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    # Length of the generated initial password handed to a FamilyAdmin once.
    ACCOUNT_INITIAL_PASSWORD_LENGTH: int = 12

    # --- Wagle realtime / Push / device PIN (Wave 3, D6) --------------------
    # These are operational knobs, not product policy. The user-facing rules
    # they touch (Push payload disclosure D6-P1, mute D6-P2, bundling D6-P3)
    # are undecided and are NOT encoded anywhere in code — see
    # `wagle/push_service.py`.
    #
    # PIN length and lock duration are config rather than constants precisely
    # because they are UX decisions nobody has made yet; the defaults mirror
    # the already-approved Account credential parameters above so that this
    # task is not quietly inventing a second, different security posture.
    WAGLE_PIN_LENGTH: int = 6
    WAGLE_PIN_MAX_ATTEMPTS: int = 5
    WAGLE_PIN_LOCK_DURATION_SECONDS: int = 300
    # How often a live WebSocket re-derives its authority from the database.
    # This is the upper bound on how long a revoked membership can still
    # receive events, so it is a security-relevant number, stated rather than
    # buried: with the default, a revocation takes effect within 15 seconds.
    WAGLE_REALTIME_REVALIDATE_SECONDS: int = 15
    # Bounded durable catch-up. Also the cross-process delivery interval — see
    # `InProcessFanout`'s docstring for why that matters under `--workers 2`.
    WAGLE_REALTIME_CATCHUP_SECONDS: int = 5
    WAGLE_PUSH_MAX_ATTEMPTS: int = 5

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
