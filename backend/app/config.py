from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Neon URLs can be pasted as-is; see app/core/db_url.py.
    DATABASE_URL: str = "postgresql+asyncpg://nexora:nexora@localhost:5432/nexora"
    # Direct (non-pooler) URL for Alembic. Falls back to DATABASE_URL when empty.
    MIGRATION_DATABASE_URL: str = ""
    # Separate database for the test suite (never the dev database).
    TEST_DATABASE_URL: str = ""

    # Comma-separated in the environment, e.g. "http://localhost:5173,https://app.example.com"
    CORS_ORIGINS: str = "http://localhost:5173"

    # Conservative pool settings for Render Free + Neon Free
    DB_POOL_SIZE: int = 2
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 300

    # Firebase Authentication
    FIREBASE_PROJECT_ID: str = ""
    # host:port of the Firebase Auth Emulator, local development only (e.g. localhost:9099).
    FIREBASE_AUTH_EMULATOR_HOST: str = ""
    # Reject tokens whose email is not verified. Disable only for local emulator use.
    AUTH_REQUIRE_VERIFIED_EMAIL: bool = True

    @field_validator("LOG_LEVEL")
    @classmethod
    def _upper_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
