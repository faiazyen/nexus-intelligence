"""Action Queue maintenance.

``refresh_action_queue`` re-scores every account in an organization,
persists a fresh ``AccountScore`` row per account, and upserts
``ActionQueueEntry`` rows for accounts at or above ``QUEUE_THRESHOLD``.

The pure helpers (strongest signal, window estimate, summary building) are
kept free of I/O so they can be unit-tested without a database.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Account, ActionQueueEntry, ICPProfile, Signal, utcnow
from app.services.scoring import (
    QUEUE_THRESHOLD,
    score_account,
    signal_strength,
    timing_window_days,
    _signal_age_days,
)

#: Fallback window estimate when an account somehow queues without signals.
DEFAULT_WINDOW_ESTIMATE_DAYS = 30

#: How many signals to mention in the queue entry's signal summary.
SUMMARY_SIGNAL_LIMIT = 3


def select_strongest_signal(
    signals: Sequence[Signal], now: datetime
) -> Optional[Signal]:
    """Return the signal with the highest strength (decay x type weight)."""
    if not signals:
        return None
    return max(signals, key=lambda s: signal_strength(s, now))


def compute_window_estimate(signal: Optional[Signal], now: datetime) -> int:
    """Days remaining in the strongest signal's timing window.

    ``window - age`` for the given signal, floored at 1 day (an expired
    window still leaves the entry actionable "now"). Returns
    ``DEFAULT_WINDOW_ESTIMATE_DAYS`` when no signal is available.
    """
    if signal is None:
        return DEFAULT_WINDOW_ESTIMATE_DAYS
    window = timing_window_days(signal.signal_type)
    age = _signal_age_days(signal, now)
    return max(1, int(round(window - age)))


def build_signal_summary(signals: Sequence[Signal], now: datetime) -> str:
    """One-line summary of the strongest signals, for the Action Queue card.

    Lists up to ``SUMMARY_SIGNAL_LIMIT`` signals, strongest first, as
    ``signal_type: title-or-summary`` segments joined by " | ".
    """
    if not signals:
        return "No active signals."
    ranked = sorted(signals, key=lambda s: signal_strength(s, now), reverse=True)
    segments = []
    for signal in ranked[:SUMMARY_SIGNAL_LIMIT]:
        label = (signal.title or signal.summary or "").strip() or "signal detected"
        if len(label) > 140:
            label = label[:137] + "..."
        segments.append(f"{signal.signal_type}: {label}")
    return " | ".join(segments)


async def refresh_action_queue(
    db: AsyncSession, org_id: uuid.UUID
) -> list[ActionQueueEntry]:
    """Re-score all accounts for an org and upsert the Action Queue.

    For every account in the organization:

    1. Score it against the org's latest ICP profile using all non-archived
       signals and persist a new ``AccountScore`` row.
    2. If the composite score is >= ``QUEUE_THRESHOLD`` (70):
       - update the existing *pending* queue entry in place if one exists
         (never duplicates pending entries), or
       - insert a new pending ``ActionQueueEntry`` with a signal summary and
         a ``days_in_window_estimate`` derived from the strongest signal's
         timing window.

    Commits the session and returns the queue entries that were created or
    refreshed, strongest score first.
    """
    now = utcnow()

    icp_result = await db.execute(
        select(ICPProfile)
        .where(ICPProfile.org_id == org_id)
        .order_by(ICPProfile.created_at.desc())
    )
    icp = icp_result.scalars().first()

    accounts_result = await db.execute(
        select(Account)
        .where(Account.org_id == org_id)
        .options(selectinload(Account.signals))
    )
    accounts = accounts_result.scalars().all()

    touched: list[ActionQueueEntry] = []
    for account in accounts:
        signals = [s for s in (account.signals or []) if s.status != "archived"]
        score = score_account(account, icp, signals, now)
        db.add(score)

        if score.composite_nexus_score < QUEUE_THRESHOLD:
            continue

        strongest = select_strongest_signal(signals, now)
        window_estimate = compute_window_estimate(strongest, now)
        summary = build_signal_summary(signals, now)

        pending_result = await db.execute(
            select(ActionQueueEntry).where(
                ActionQueueEntry.account_id == account.id,
                ActionQueueEntry.status == "pending",
            )
        )
        entry = pending_result.scalars().first()

        if entry is None:
            entry = ActionQueueEntry(
                account_id=account.id,
                nexus_score=score.composite_nexus_score,
                signal_summary=summary,
                days_in_window_estimate=window_estimate,
                entered_queue_at=now,
                status="pending",
            )
            db.add(entry)
        else:
            entry.nexus_score = score.composite_nexus_score
            entry.signal_summary = summary
            entry.days_in_window_estimate = window_estimate
        touched.append(entry)

    await db.commit()
    touched.sort(key=lambda e: e.nexus_score or 0, reverse=True)
    return touched
