"""Analytics routes: pipeline funnel, signal distribution, audit trail, LLM cost."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_router import cost_tracker
from app.db.models import (
    Account,
    AccountScore,
    ActionQueueEntry,
    Organization,
    OutreachDraft,
    PipelineEvent,
    Signal,
    utcnow,
)
from app.db.session import get_db
from app.routers.deps import get_current_org

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/pipeline")
async def pipeline_funnel(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Conversion funnel: signals -> classified -> scored -> queued -> outreach -> contacted -> replied."""
    org_account_ids = select(Account.id).where(Account.org_id == org.id)

    total_signals = (
        await db.execute(
            select(func.count(Signal.id)).where(Signal.account_id.in_(org_account_ids))
        )
    ).scalar() or 0
    classified = (
        await db.execute(
            select(func.count(Signal.id)).where(
                Signal.account_id.in_(org_account_ids),
                Signal.status.in_(["classified", "scored"]),
            )
        )
    ).scalar() or 0
    scored_accounts = (
        await db.execute(
            select(func.count(func.distinct(AccountScore.account_id))).where(
                AccountScore.account_id.in_(org_account_ids)
            )
        )
    ).scalar() or 0
    queued = (
        await db.execute(
            select(func.count(ActionQueueEntry.id)).where(
                ActionQueueEntry.account_id.in_(org_account_ids)
            )
        )
    ).scalar() or 0
    outreach_generated = (
        await db.execute(
            select(func.count(func.distinct(OutreachDraft.account_id))).where(
                OutreachDraft.account_id.in_(org_account_ids)
            )
        )
    ).scalar() or 0
    contacted = (
        await db.execute(
            select(func.count(func.distinct(OutreachDraft.account_id))).where(
                OutreachDraft.account_id.in_(org_account_ids),
                OutreachDraft.sent_at.is_not(None),
            )
        )
    ).scalar() or 0
    replied = (
        await db.execute(
            select(func.count(func.distinct(OutreachDraft.account_id))).where(
                OutreachDraft.account_id.in_(org_account_ids),
                OutreachDraft.outcome.in_(["replied", "meeting_booked"]),
            )
        )
    ).scalar() or 0

    return {
        "funnel": [
            {"stage": "signals_detected", "count": total_signals},
            {"stage": "signals_classified", "count": classified},
            {"stage": "accounts_scored", "count": scored_accounts},
            {"stage": "accounts_queued", "count": queued},
            {"stage": "outreach_generated", "count": outreach_generated},
            {"stage": "contacted", "count": contacted},
            {"stage": "replied", "count": replied},
        ]
    }


@router.get("/signals")
async def signal_distribution(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Signal counts by type and urgency tier over the last 30 days."""
    since = utcnow() - timedelta(days=30)
    org_account_ids = select(Account.id).where(Account.org_id == org.id)

    by_type_rows = (
        await db.execute(
            select(Signal.signal_type, func.count(Signal.id))
            .where(Signal.account_id.in_(org_account_ids), Signal.detected_at >= since)
            .group_by(Signal.signal_type)
        )
    ).all()
    by_tier_rows = (
        await db.execute(
            select(Signal.urgency_tier, func.count(Signal.id))
            .where(Signal.account_id.in_(org_account_ids), Signal.detected_at >= since)
            .group_by(Signal.urgency_tier)
        )
    ).all()

    return {
        "window_days": 30,
        "by_type": [{"signal_type": t, "count": c} for t, c in by_type_rows],
        "by_tier": [
            {"urgency_tier": tier or "unclassified", "count": c}
            for tier, c in by_tier_rows
        ],
    }


@router.get("/pipeline-events")
async def pipeline_events(
    limit: int = 50,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Recent pipeline-level audit events (collector failures, budget
    stops) — so a day's run is never an unexplained black box. Per-call
    LLM routing/fallback detail lives in GET /analytics/costs instead."""
    rows = (
        (
            await db.execute(
                select(PipelineEvent)
                .where(PipelineEvent.org_id == org.id)
                .order_by(desc(PipelineEvent.created_at))
                .limit(min(limit, 200))
            )
        )
        .scalars()
        .all()
    )
    return {
        "events": [
            {
                "id": str(row.id),
                "event_type": row.event_type,
                "detail": row.detail,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
    }


@router.get("/costs")
async def llm_costs(
    org: Organization = Depends(get_current_org),
) -> dict:
    """Today's LLM spend broken down by model and by purpose, with any
    Tier 3 (Claude) fallback events highlighted."""
    return cost_tracker.today_summary(str(org.id))
