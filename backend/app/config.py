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

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
