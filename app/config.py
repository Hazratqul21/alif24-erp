from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://erp_user:erp_password@localhost:5432/alif24_erp"
    ALIF24_DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Super Admin
    SUPER_ADMIN_EMAIL: str = "admin@alif24.uz"
    SUPER_ADMIN_PASSWORD: str = "change-me"

    # Eskiz SMS
    ESKIZ_EMAIL: Optional[str] = None
    ESKIZ_PASSWORD: Optional[str] = None
    ESKIZ_BASE_URL: str = "https://notify.eskiz.uz/api"

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@alif24.uz"

    # Payment Gateways
    PAYME_MERCHANT_ID: Optional[str] = None
    PAYME_SECRET_KEY: Optional[str] = None
    CLICK_MERCHANT_ID: Optional[str] = None
    CLICK_SERVICE_ID: Optional[str] = None
    CLICK_SECRET_KEY: Optional[str] = None
    UZUM_MERCHANT_ID: Optional[str] = None
    UZUM_SECRET_KEY: Optional[str] = None

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "/data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    BASE_DOMAIN: str = "alif24.uz"
    API_PREFIX: str = "/api/v1"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
