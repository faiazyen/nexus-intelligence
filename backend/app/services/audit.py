"""Minimal pipeline audit trail.

Fine-grained, per-LLM-call routing detail (which tier/model handled a
call, whether a fallback was used, real cost) already lives in
llm_router's JSONL cost log and is queryable via GET /api/v1/costs.
``pipeline_events`` is deliberately scoped one level up: pipeline-level
degradation (a collector failing, a stage being skipped over budget) so
a day's run is never an unexplained black box even without opening logs.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PipelineEvent


async def log_pipeline_event(
    db: AsyncSession, org_id: uuid.UUID, event_type: str, detail: dict
) -> None:
    """Persist one audit row. Never raises — a logging failure must not
    take down the pipeline it's trying to document."""
    try:
        db.add(PipelineEvent(org_id=org_id, event_type=event_type, detail=detail))
        await db.commit()
    except Exception:  # noqa: BLE001
        await db.rollback()
