"""NEXUS INTENT routes: action queue, account profiles, outreach, ICP."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Account,
    AccountScore,
    ActionQueueEntry,
    ICPProfile,
    Organization,
    OutreachDraft,
    Signal,
)
from app.db.session import get_db
from app.routers.deps import get_current_org

router = APIRouter(prefix="/intent", tags=["intent"])


def _serialize_signal(signal: Signal) -> dict:
    return {
        "id": str(signal.id),
        "signal_type": signal.signal_type,
        "source": signal.source,
        "title": signal.title,
        "summary": signal.summary,
        "urgency_tier": signal.urgency_tier,
        "budget_implication": signal.budget_implication,
        "decision_maker_involved": signal.decision_maker_involved,
        "days_to_action_window": signal.days_to_action_window,
        "detected_at": signal.detected_at.isoformat() if signal.detected_at else None,
        "status": signal.status,
    }


def _serialize_draft(draft: OutreachDraft) -> dict:
    return {
        "id": str(draft.id),
        "variant": draft.variant,
        "email_subject": draft.email_subject,
        "email_body": draft.email_body,
        "linkedin_message": draft.linkedin_message,
        "call_script": draft.call_script,
        "positioning_frame": draft.positioning_frame,
        "signal_reference": draft.signal_reference,
        "sent_at": draft.sent_at.isoformat() if draft.sent_at else None,
        "outcome": draft.outcome,
        "created_at": draft.created_at.isoformat() if draft.created_at else None,
    }


def _serialize_score(score: Optional[AccountScore]) -> Optional[dict]:
    if score is None:
        return None
    return {
        "urgency": score.urgency,
        "fit": score.fit,
        "budget_probability": score.budget_probability,
        "composite_nexus_score": score.composite_nexus_score,
        "explanation": score.explanation,
        "scored_at": score.scored_at.isoformat() if score.scored_at else None,
    }


async def _latest_score(db: AsyncSession, account_id: uuid.UUID) -> Optional[AccountScore]:
    result = await db.execute(
        select(AccountScore)
        .where(AccountScore.account_id == account_id)
        .order_by(AccountScore.scored_at.desc())
        .limit(1)
    )
    return result.scalars().first()


@router.get("/queue")
async def action_queue(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Today's Action Queue: hot accounts, strongest score first."""
    result = await db.execute(
        select(ActionQueueEntry, Account)
        .join(Account, ActionQueueEntry.account_id == Account.id)
        .where(
            Account.org_id == org.id,
            ActionQueueEntry.status.in_(["pending", "outreach_generated"]),
        )
        .order_by(ActionQueueEntry.nexus_score.desc())
    )
    entries = []
    for entry, account in result.all():
        score = await _latest_score(db, account.id)
        signals = (
            (
                await db.execute(
                    select(Signal)
                    .where(Signal.account_id == account.id, Signal.status != "archived")
                    .order_by(Signal.detected_at.desc())
                    .limit(5)
                )
            )
            .scalars()
            .all()
        )
        entries.append(
            {
                "id": str(entry.id),
                "nexus_score": entry.nexus_score,
                "signal_summary": entry.signal_summary,
                "days_in_window_estimate": entry.days_in_window_estimate,
                "entered_queue_at": entry.entered_queue_at.isoformat()
                if entry.entered_queue_at
                else None,
                "status": entry.status,
                "account": {
                    "id": str(account.id),
                    "company_name": account.company_name,
                    "domain": account.domain,
                    "industry": account.industry,
                    "employee_count": account.employee_count,
                    "geography": account.geography,
                },
                "score": _serialize_score(score),
                "signals": [_serialize_signal(s) for s in signals],
            }
        )
    return {"entries": entries, "count": len(entries)}


@router.get("/account/{account_id}")
async def account_profile(
    account_id: uuid.UUID,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Full account profile: signal timeline, score history, outreach drafts."""
    account = (
        await db.execute(
            select(Account).where(Account.id == account_id, Account.org_id == org.id)
        )
    ).scalars().first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    signals = (
        (
            await db.execute(
                select(Signal)
                .where(Signal.account_id == account_id)
                .order_by(Signal.detected_at.desc())
            )
        )
        .scalars()
        .all()
    )
    scores = (
        (
            await db.execute(
                select(AccountScore)
                .where(AccountScore.account_id == account_id)
                .order_by(AccountScore.scored_at.desc())
                .limit(10)
            )
        )
        .scalars()
        .all()
    )
    drafts = (
        (
            await db.execute(
                select(OutreachDraft)
                .where(OutreachDraft.account_id == account_id)
                .order_by(OutreachDraft.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    return {
        "account": {
            "id": str(account.id),
            "company_name": account.company_name,
            "domain": account.domain,
            "industry": account.industry,
            "employee_count": account.employee_count,
            "revenue_estimate": account.revenue_estimate,
            "geography": account.geography,
            "tech_stack": account.tech_stack,
        },
        "latest_score": _serialize_score(scores[0] if scores else None),
        "score_history": [_serialize_score(s) for s in scores],
        "signals": [_serialize_signal(s) for s in signals],
        "outreach_drafts": [_serialize_draft(d) for d in drafts],
    }


@router.post("/outreach/{account_id}")
async def generate_outreach_route(
    account_id: uuid.UUID,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate the 3-variant outreach package for an account."""
    account = (
        await db.execute(
            select(Account).where(Account.id == account_id, Account.org_id == org.id)
        )
    ).scalars().first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found.")

    try:
        from app.agents.interface import generate_outreach
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"Agent system unavailable: {exc}")
    try:
        drafts = await generate_outreach(account_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"drafts": [_serialize_draft(d) for d in drafts]}


class ICPRequest(BaseModel):
    target_industries: list[str] = Field(default_factory=list)
    company_size_min: int = Field(default=10, ge=1)
    company_size_max: int = Field(default=1000, ge=1)
    titles_targeted: list[str] = Field(default_factory=list)
    geographies: list[str] = Field(default_factory=list)
    tech_stack_keywords: list[str] = Field(default_factory=list)
    offer_description: str = ""


@router.put("/icp")
async def upsert_icp(
    payload: ICPRequest,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create or update the organization's ICP profile."""
    existing = (
        await db.execute(
            select(ICPProfile)
            .where(ICPProfile.org_id == org.id)
            .order_by(ICPProfile.created_at.desc())
        )
    ).scalars().first()

    if existing is None:
        existing = ICPProfile(org_id=org.id)
        db.add(existing)

    existing.target_industries = payload.target_industries
    existing.company_size_min = payload.company_size_min
    existing.company_size_max = payload.company_size_max
    existing.titles_targeted = payload.titles_targeted
    existing.geographies = payload.geographies
    existing.tech_stack_keywords = payload.tech_stack_keywords
    existing.offer_description = payload.offer_description
    await db.commit()
    return {"id": str(existing.id), "status": "saved"}


@router.post("/pipeline/run")
async def trigger_pipeline(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Manually trigger a full supervisor cycle (scout -> classify -> score)."""
    try:
        from app.agents.interface import run_pipeline
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=f"Agent system unavailable: {exc}")
    return await run_pipeline(org.id, db)
