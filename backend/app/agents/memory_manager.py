"""AGENT 6 — Memory Manager.

Closes the learning loop: records outreach outcomes, tracks which signal
types actually predicted conversions, and maintains per-org scoring weight
adjustments in ``Organization.settings["signal_weight_adjustments"]`` —
the rolling "win DNA" per organization.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.db.models import Account, Organization, OutreachDraft, Signal, utcnow

logger = logging.getLogger("nexus.agents.memory")

#: Outcomes that indicate the signal successfully predicted buyer intent.
POSITIVE_OUTCOMES = ("replied", "meeting_booked")
NEGATIVE_OUTCOMES = ("no_response", "bounced")
VALID_OUTCOMES = POSITIVE_OUTCOMES + NEGATIVE_OUTCOMES

#: Weight adjustment step per outcome, bounded to keep learning conservative.
ADJUSTMENT_STEP = 1
ADJUSTMENT_BOUND = 10


def apply_adjustment(current: int, outcome: str) -> int:
    """New bounded adjustment value for a signal type given one outcome."""
    if outcome in POSITIVE_OUTCOMES:
        return min(ADJUSTMENT_BOUND, current + ADJUSTMENT_STEP)
    if outcome in NEGATIVE_OUTCOMES:
        return max(-ADJUSTMENT_BOUND, current - ADJUSTMENT_STEP)
    return current


async def record_outcome(
    draft_id: uuid.UUID, outcome: str, db: AsyncSession
) -> Optional[OutreachDraft]:
    """Record an outreach outcome and update the org's signal-weight memory.

    Sets ``outcome`` (and ``reply_received_at`` for positive outcomes) on the
    draft, then nudges the org's per-signal-type weight adjustment up or down
    and appends an entry to the org's outcome history.
    """
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"Invalid outcome '{outcome}'. Expected one of {VALID_OUTCOMES}.")

    draft = (
        await db.execute(select(OutreachDraft).where(OutreachDraft.id == draft_id))
    ).scalars().first()
    if draft is None:
        return None

    draft.outcome = outcome
    if outcome in POSITIVE_OUTCOMES:
        draft.reply_received_at = utcnow()

    account = (
        await db.execute(select(Account).where(Account.id == draft.account_id))
    ).scalars().first()
    if account is None:
        await db.commit()
        return draft

    # The strongest recent signal is credited/blamed for the outcome.
    signal = (
        await db.execute(
            select(Signal)
            .where(Signal.account_id == account.id)
            .order_by(Signal.detected_at.desc())
        )
    ).scalars().first()

    org = (
        await db.execute(select(Organization).where(Organization.id == account.org_id))
    ).scalars().first()
    if org is not None and signal is not None:
        org_settings = dict(org.settings or {})
        adjustments = dict(org_settings.get("signal_weight_adjustments", {}))
        current = int(adjustments.get(signal.signal_type, 0))
        adjustments[signal.signal_type] = apply_adjustment(current, outcome)
        history = list(org_settings.get("outcome_history", []))
        history.append(
            {
                "draft_id": str(draft.id),
                "account": account.company_name,
                "signal_type": signal.signal_type,
                "variant": draft.variant,
                "outcome": outcome,
                "at": utcnow().isoformat(),
            }
        )
        org_settings["signal_weight_adjustments"] = adjustments
        org_settings["outcome_history"] = history[-200:]
        org.settings = org_settings
        flag_modified(org, "settings")
        logger.info(
            "Memory Manager: %s outcome for %s adjusts %s weight to %+d",
            outcome, account.company_name, signal.signal_type,
            adjustments[signal.signal_type],
        )

    await db.commit()
    return draft
