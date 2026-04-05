from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    MAX_LOGIN_ATTEMPTS: int = 5
    LOCK_DURATION_SECONDS: int = 300

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://point-festival.exiledstarbee.synology.me"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
