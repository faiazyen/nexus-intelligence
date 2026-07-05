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
    # Redis was dropped along with the old direct-Anthropic cost tracker it
    # backed (see app/core/llm_router.py's file-based CostTracker instead).
    qdrant_url: str = "http://localhost:6333"

    # All LLM calls route through OpenRouter (one key, one SDK) — see
    # app/core/llm_router.py. Slugs default to what was verified against
    # OpenRouter's live /api/v1/models catalog; override per-env if that
    # catalog has moved on by the time this runs.
    openrouter_api_key: str = ""
    nexus_llm_classifier: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    nexus_llm_classifier_fallback: str = "deepseek/deepseek-v4-flash"
    nexus_llm_outreach: str = "moonshotai/kimi-k2-thinking"
    nexus_llm_brain: str = "moonshotai/kimi-k2-thinking"
    nexus_llm_fallback: str = "anthropic/claude-opus-4.8"
    # Hard daily spend limit (USD) before routing drops to free-tier/rule-
    # based paths only. Revised down from the pre-OpenRouter $0.50 default
    # now that a real per-request cost is available to enforce against.
    nexus_daily_llm_limit: float = 0.25
    # Skips the anthropic/* fallback slug entirely (still via OpenRouter,
    # not a separate key) — for pure non-Claude beta cost testing.
    nexus_disable_claude: bool = False

    apollo_api_key: str = ""
    newsapi_key: str = ""
    crunchbase_api_key: str = ""

    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
