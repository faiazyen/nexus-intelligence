"""NEXUS scoring engine.

Implements the exact contract from docs/CONTRACT.md:

- ``compute_urgency(signals, now) -> int``          (0-100)
- ``compute_fit(account, icp) -> int``              (0-100)
- ``compute_budget_probability(signals) -> int``    (0-100, additive, caps at 100)
- ``compute_nexus_score(urgency, fit, budget)``     ((u*f*b)/10000, 0-100)
- ``QUEUE_THRESHOLD = 70``
- ``SIGNAL_BUDGET_WEIGHTS`` / ``TIMING_WINDOWS_DAYS`` per contract

Plus a ``score_account`` convenience that assembles a persistable
``AccountScore`` row with a human-readable explanation.

All functions are pure (no I/O, no database) so they are unit-testable with
in-memory model objects.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable, Optional, Sequence

from app.db.models import Account, AccountScore, ICPProfile, Signal

# --- Contract constants (docs/CONTRACT.md — do not change) -----------------

QUEUE_THRESHOLD = 70

SIGNAL_BUDGET_WEIGHTS = {
    "job_post": 15,
    "funding": 25,
    "leadership_change": 20,
    "earnings_language": 30,
    "procurement_notice": 40,
    "tech_change": 10,
    "news": 5,
    "filing": 10,
}

TIMING_WINDOWS_DAYS = {
    "leadership_change": 90,
    "funding": 60,
    "job_post": 45,
    "procurement_notice": 120,
    "earnings_language": 60,
    "tech_change": 45,
    "news": 30,
    "filing": 90,
}

CANONICAL_SIGNAL_TYPES = tuple(SIGNAL_BUDGET_WEIGHTS)

# --- Tunable internals ------------------------------------------------------

#: Weight applied to signal types not present in SIGNAL_BUDGET_WEIGHTS.
DEFAULT_BUDGET_WEIGHT = 5

#: Timing window applied to signal types not present in TIMING_WINDOWS_DAYS.
DEFAULT_TIMING_WINDOW_DAYS = 30

#: Each additional concurrently-active signal boosts urgency by this factor.
CONCURRENT_SIGNAL_BONUS = 0.15

#: Ceiling for the concurrent-signal multiplier.
CONCURRENT_MULTIPLIER_CAP = 1.5

#: Fit dimension weights; they sum to 100.
FIT_WEIGHTS = {"industry": 35, "size": 25, "geography": 20, "tech_stack": 20}

#: Partial credit when company size falls outside the ICP range but within 2x.
SIZE_NEAR_MISS_POINTS = 10

#: Fit returned when no ICP profile exists yet (neutral, not zero — a missing
#: ICP should not silently null out every account's composite score).
NEUTRAL_FIT_NO_ICP = 50

_MAX_TYPE_WEIGHT = max(SIGNAL_BUDGET_WEIGHTS.values())


# --- Helpers ----------------------------------------------------------------


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    """Round ``value`` and clamp it to the inclusive [low, high] range."""
    return max(low, min(high, int(round(value))))


def _signal_age_days(signal: Signal, now: datetime) -> float:
    """Age of a signal in fractional days; unknown detection time counts as fresh."""
    detected = signal.detected_at
    if detected is None:
        return 0.0
    if detected.tzinfo is None:
        detected = detected.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return max(0.0, (now - detected).total_seconds() / 86400.0)


def timing_window_days(signal_type: str) -> int:
    """Timing window (days) for a signal type, with a safe default."""
    return TIMING_WINDOWS_DAYS.get(signal_type, DEFAULT_TIMING_WINDOW_DAYS)


def recency_decay(signal: Signal, now: datetime) -> float:
    """Recency factor in [0.0, 1.0] for a signal.

    A signal carries full weight while inside its timing window, then decays
    linearly to zero over one additional window length. A signal older than
    twice its window contributes nothing.
    """
    window = float(timing_window_days(signal.signal_type))
    age = _signal_age_days(signal, now)
    if age <= window:
        return 1.0
    overage = age - window
    return max(0.0, 1.0 - overage / window)


def signal_strength(signal: Signal, now: datetime) -> float:
    """Normalized strength in [0.0, 1.0]: recency decay x relative type weight.

    Type weight is normalized against the heaviest signal type so a fresh
    ``procurement_notice`` (weight 40) has strength 1.0 while a fresh ``news``
    item (weight 5) has strength 0.125.
    """
    weight = SIGNAL_BUDGET_WEIGHTS.get(signal.signal_type, DEFAULT_BUDGET_WEIGHT)
    return recency_decay(signal, now) * (weight / _MAX_TYPE_WEIGHT)


def _active_signal_count(signals: Iterable[Signal], now: datetime) -> int:
    """Number of signals still inside their own timing window."""
    return sum(
        1
        for s in signals
        if _signal_age_days(s, now) <= timing_window_days(s.signal_type)
    )


# --- Contract functions -----------------------------------------------------


def compute_urgency(signals: list[Signal], now: datetime) -> int:
    """Urgency score 0-100.

    Formula: recency decay x type weight x concurrent-signal multiplier.

    - The base is the single strongest signal (decay x normalized type
      weight, scaled to 0-100).
    - Each additional signal still inside its timing window adds
      ``CONCURRENT_SIGNAL_BONUS`` to the multiplier (capped at
      ``CONCURRENT_MULTIPLIER_CAP``) — several concurrent triggers indicate a
      hotter account than one trigger alone.
    """
    if not signals:
        return 0
    base = max(signal_strength(s, now) for s in signals) * 100.0
    active = _active_signal_count(signals, now)
    multiplier = min(
        CONCURRENT_MULTIPLIER_CAP,
        1.0 + CONCURRENT_SIGNAL_BONUS * max(active - 1, 0),
    )
    return _clamp(base * multiplier)


def fit_components(account: Account, icp: ICPProfile) -> dict:
    """Per-dimension fit points for an account against an ICP.

    Returns a dict with keys ``industry``, ``size``, ``geography`` and
    ``tech_stack`` whose values sum to the fit score. Unconstrained ICP
    dimensions (empty lists) award full points — no constraint means every
    account satisfies it.
    """
    points: dict = {}

    # Industry: exact or substring match, case-insensitive.
    industry = (account.industry or "").strip().lower()
    targets = [t.strip().lower() for t in (icp.target_industries or []) if t and t.strip()]
    if not targets:
        points["industry"] = FIT_WEIGHTS["industry"]
    elif industry and any(t == industry or t in industry or industry in t for t in targets):
        points["industry"] = FIT_WEIGHTS["industry"]
    else:
        points["industry"] = 0

    # Size: full points inside [min, max]; partial credit within a 2x band.
    count = account.employee_count or 0
    size_min = icp.company_size_min if icp.company_size_min is not None else 0
    size_max = icp.company_size_max if icp.company_size_max is not None else 10**9
    if count <= 0:
        points["size"] = 0
    elif size_min <= count <= size_max:
        points["size"] = FIT_WEIGHTS["size"]
    elif (size_min / 2.0) <= count <= (size_max * 2.0):
        points["size"] = SIZE_NEAR_MISS_POINTS
    else:
        points["size"] = 0

    # Geography: substring match either direction, case-insensitive.
    geography = (account.geography or "").strip().lower()
    geos = [g.strip().lower() for g in (icp.geographies or []) if g and g.strip()]
    if not geos:
        points["geography"] = FIT_WEIGHTS["geography"]
    elif geography and any(g == geography or g in geography or geography in g for g in geos):
        points["geography"] = FIT_WEIGHTS["geography"]
    else:
        points["geography"] = 0

    # Tech stack: fraction of ICP keywords found anywhere in the account's
    # tech_stack JSON (keys and values), case-insensitive.
    keywords = [k.strip().lower() for k in (icp.tech_stack_keywords or []) if k and k.strip()]
    if not keywords:
        points["tech_stack"] = FIT_WEIGHTS["tech_stack"]
    else:
        try:
            blob = json.dumps(account.tech_stack or {}).lower()
        except (TypeError, ValueError):
            blob = str(account.tech_stack or "").lower()
        matched = sum(1 for k in keywords if k in blob)
        points["tech_stack"] = int(round(FIT_WEIGHTS["tech_stack"] * matched / len(keywords)))

    return points


def compute_fit(account: Account, icp: Optional[ICPProfile]) -> int:
    """Fit score 0-100: weighted sum of industry, size, geography, tech stack.

    Weights (sum 100): industry 35, size 25, geography 20, tech stack 20.
    If no ICP exists yet, returns a neutral ``NEUTRAL_FIT_NO_ICP`` (50).
    """
    if icp is None:
        return NEUTRAL_FIT_NO_ICP
    return _clamp(sum(fit_components(account, icp).values()))


def budget_components(signals: Iterable[Signal]) -> list:
    """(signal_type, weight) contribution pairs, one per signal, uncapped."""
    return [
        (s.signal_type, SIGNAL_BUDGET_WEIGHTS.get(s.signal_type, DEFAULT_BUDGET_WEIGHT))
        for s in signals
    ]


def compute_budget_probability(signals: list[Signal]) -> int:
    """Budget probability 0-100.

    Additive per-signal-type weights: every signal contributes its type's
    weight from ``SIGNAL_BUDGET_WEIGHTS`` (unknown types contribute
    ``DEFAULT_BUDGET_WEIGHT``); the sum is capped at 100.
    """
    total = sum(weight for _, weight in budget_components(signals))
    return _clamp(total)


def compute_nexus_score(urgency: int, fit: int, budget: int) -> int:
    """Composite NEXUS score: (urgency x fit x budget) / 10000, clamped 0-100.

    Inputs are clamped to [0, 100] first so out-of-range values can never
    produce a composite outside the scale.
    """
    u = _clamp(urgency)
    f = _clamp(fit)
    b = _clamp(budget)
    return _clamp((u * f * b) / 10000.0)


# --- Convenience ------------------------------------------------------------


def _strongest(signals: Sequence[Signal], now: datetime) -> Optional[Signal]:
    """The signal with the highest strength, or None for an empty sequence."""
    if not signals:
        return None
    return max(signals, key=lambda s: signal_strength(s, now))


def score_account(
    account: Account,
    icp: Optional[ICPProfile],
    signals: list[Signal],
    now: datetime,
) -> AccountScore:
    """Score an account and return a persistable ``AccountScore`` row.

    The returned object is NOT added to any session — the caller decides
    whether and where to persist it. The ``explanation`` field is a
    human-readable breakdown of how each dimension was derived.
    """
    urgency = compute_urgency(signals, now)
    fit = compute_fit(account, icp)
    budget = compute_budget_probability(signals)
    composite = compute_nexus_score(urgency, fit, budget)

    parts = [
        f"NEXUS {composite}/100 = urgency {urgency} x fit {fit} x budget {budget} / 10000."
    ]

    strongest = _strongest(signals, now)
    active = _active_signal_count(signals, now)
    if strongest is not None:
        parts.append(
            f"Urgency: {len(signals)} signal(s), {active} inside timing window; "
            f"strongest is {strongest.signal_type} "
            f"({timing_window_days(strongest.signal_type)}-day window)."
        )
    else:
        parts.append("Urgency: no signals detected for this account.")

    if icp is not None:
        fc = fit_components(account, icp)
        parts.append(
            "Fit: industry {i}/{iw}, size {s}/{sw}, geography {g}/{gw}, "
            "tech stack {t}/{tw}.".format(
                i=fc["industry"],
                iw=FIT_WEIGHTS["industry"],
                s=fc["size"],
                sw=FIT_WEIGHTS["size"],
                g=fc["geography"],
                gw=FIT_WEIGHTS["geography"],
                t=fc["tech_stack"],
                tw=FIT_WEIGHTS["tech_stack"],
            )
        )
    else:
        parts.append(f"Fit: no ICP profile configured; neutral {NEUTRAL_FIT_NO_ICP} applied.")

    contributions = budget_components(signals)
    if contributions:
        listing = ", ".join(f"{stype} +{weight}" for stype, weight in contributions)
        raw_total = sum(weight for _, weight in contributions)
        capped = " (capped at 100)" if raw_total > 100 else ""
        parts.append(f"Budget: {listing} = {raw_total}{capped}.")
    else:
        parts.append("Budget: no budget-implying signals.")

    return AccountScore(
        account_id=account.id,
        urgency=urgency,
        fit=fit,
        budget_probability=budget,
        composite_nexus_score=composite,
        signal_ids=[str(s.id) for s in signals if s.id is not None],
        explanation=" ".join(parts),
        scored_at=now,
    )
