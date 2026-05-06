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

_INSECURE_JWT_DEFAULT = "change-me-to-a-random-64-char-string"
_INSECURE_SUPER_ADMIN_DEFAULT = "change-me"


def validate_production_config() -> None:
    """Production muhitida xavfsizlik tekshiruvi.
    Bu funksiya faqat uvicorn ishga tushganda chaqiriladi (alembic import paytida emas).
    """
    if settings.APP_ENV != "production":
        return
    problems = []
    if settings.JWT_SECRET_KEY == _INSECURE_JWT_DEFAULT or len(settings.JWT_SECRET_KEY) < 32:
        problems.append("JWT_SECRET_KEY must be set to a strong random value (>=32 chars)")
    if settings.SUPER_ADMIN_PASSWORD == _INSECURE_SUPER_ADMIN_DEFAULT or len(settings.SUPER_ADMIN_PASSWORD) < 10:
        problems.append("SUPER_ADMIN_PASSWORD must be set (>=10 chars)")
    if problems:
        raise RuntimeError(
            "Insecure configuration in production: " + "; ".join(problems)
        )
