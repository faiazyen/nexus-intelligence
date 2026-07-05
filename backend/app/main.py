"""NEXUS Intelligence API — FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import dispose_engine
from app.routers import analytics, brain, intent, signals

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("nexus.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks. Never blocks startup on external services."""
    logger.info(
        "%s starting (env=%s, llm=%s)",
        settings.app_name,
        settings.environment,
        "live" if settings.anthropic_api_key else "demo mode",
    )
    yield
    await dispose_engine()
    logger.info("%s stopped", settings.app_name)


app = FastAPI(
    title="NEXUS Intelligence API",
    description="Pre-RFP signal intelligence: monitor, reason, score, act.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brain.router, prefix="/api/v1")
app.include_router(intent.router, prefix="/api/v1")
app.include_router(signals.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict:
    """Liveness probe."""
    return {"status": "ok"}
