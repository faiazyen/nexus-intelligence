"""AGENT 3 — Account Scorer.

Nightly (and on-demand) orchestration around the pure scoring engine:
re-scores every account, refreshes the Action Queue, and marks classified
signals as scored. The math lives in ``app.services.scoring``; this agent
only sequences it.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import compile_pipeline
from app.db.models import Account, Signal

logger = logging.getLogger("nexus.agents.scorer")


async def _node_refresh_queue(state: dict) -> dict:
    """Score all accounts and upsert queue entries via the queue service."""
    from app.services.queue import refresh_action_queue

    db: AsyncSession = state["db"]
    org_id: uuid.UUID = state["org_id"]
    entries = await refresh_action_queue(db, org_id)
    return {"queued_entries": entries, "queued_count": len(entries)}


async def _node_mark_scored(state: dict) -> dict:
    """Advance classified signals to ``scored`` for this org's accounts."""
    db: AsyncSession = state["db"]
    org_id: uuid.UUID = state["org_id"]
    signals = (
        (
            await db.execute(
                select(Signal)
                .join(Account, Signal.account_id == Account.id)
                .where(Account.org_id == org_id, Signal.status == "classified")
            )
        )
        .scalars()
        .all()
    )
    for signal in signals:
        signal.status = "scored"
    await db.commit()
    logger.info("Account Scorer: marked %d signals scored", len(signals))
    return {"scored_signal_count": len(signals)}


PIPELINE_NODES = [
    ("refresh_queue", _node_refresh_queue),
    ("mark_scored", _node_mark_scored),
]


async def run_account_scorer(org_id: uuid.UUID, db: AsyncSession) -> dict:
    """Execute scoring + queue refresh for one organization."""
    pipeline = compile_pipeline("account_scorer", PIPELINE_NODES)
    return await pipeline.ainvoke({"org_id": org_id, "db": db})
