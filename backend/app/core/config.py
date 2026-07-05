"""NEXUS Intelligence — application settings.

Loaded once via pydantic-settings; every module imports `settings` from here.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env normally lives at the repo root (docker-compose reads it from there and
# injects real env vars into containers, where this list is irrelevant).
# Local, non-Docker runs are commonly launched from backend/ (as the README's
# `cd backend && uvicorn ...` does), where a bare "./.env" would never be
# found. Listing both the repo root and backend/ makes either cwd work.
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILES = (str(_BACKEND_DIR.parent / ".env"), str(_BACKEND_DIR / ".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILES, extra="ignore")

    app_name: str = "NEXUS Intelligence"
    environment: str = "development"  # development|staging|production
    debug: bool = True

    database_url: str = "postgresql+asyncpg://nexus:nexus@localhost:5432/nexus"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    anthropic_api_key: str = ""
    model_opus: str = "claude-opus-4-8"
    model_sonnet: str = "claude-sonnet-5"
    model_haiku: str = "claude-haiku-4-5-20251001"

    apollo_api_key: str = ""
    newsapi_key: str = ""
    crunchbase_api_key: str = ""

    cors_origins: str = "http://localhost:3000"

    # Cost guardrail: max daily Claude spend per 100-account org (USD)
    daily_llm_budget_usd: float = 0.50


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
