"""Analytics routes: pipeline funnel and signal distribution."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Account,
    AccountScore,
    ActionQueueEntry,
    Organization,
    OutreachDraft,
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
