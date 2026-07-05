"""AGENT 2 — Intent Classifier.

Event-driven: takes signals with status ``new``, classifies each with Claude
Haiku (cost-efficient) using the verbatim Signal Classifier prompt, and
writes urgency tier, budget implication, decision-maker flag, action window,
and a one-line summary back to the row. Status ``new`` -> ``classified``.

When no API key is configured, a deterministic heuristic classifier stands
in so the downstream pipeline still functions.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import compile_pipeline
from app.core.config import settings
from app.core.llm import claude_call
from app.core.prompts import SIGNAL_CLASSIFIER_SYSTEM_PROMPT
from app.db.models import Signal, utcnow

logger = logging.getLogger("nexus.agents.classifier")

VALID_TIERS = ("HOT", "WARM", "COOL")
VALID_BUDGET = ("CONFIRMED", "PROBABLE", "POSSIBLE", "NONE")

# Heuristic fallbacks per signal type (used in demo mode / on parse failure).
_HEURISTIC = {
    "procurement_notice": ("HOT", "CONFIRMED", True, 120),
    "earnings_language": ("HOT", "CONFIRMED", True, 60),
    "funding": ("HOT", "PROBABLE", True, 60),
    "leadership_change": ("WARM", "PROBABLE", True, 90),
    "job_post": ("WARM", "PROBABLE", False, 45),
    "tech_change": ("WARM", "POSSIBLE", False, 45),
    "filing": ("WARM", "POSSIBLE", True, 90),
    "news": ("COOL", "POSSIBLE", False, 30),
}
_DEFAULT_HEURISTIC = ("COOL", "NONE", False, 30)


def extract_json(text: str) -> Optional[dict]:
    """Parse the first JSON object found in ``text``, tolerating prose around it.

    Tries a straight ``json.loads`` first, then falls back to extracting the
    outermost ``{...}`` block with a regex. Returns None if nothing parses.
    """
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, TypeError):
        pass
    match = re.search(r"\{.*\}", text or "", re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def heuristic_classification(signal: Signal) -> dict:
    """Deterministic classification from the signal type alone."""
    tier, budget, dm, window = _HEURISTIC.get(signal.signal_type, _DEFAULT_HEURISTIC)
    return {
        "signal_type": signal.signal_type,
        "urgency_tier": tier,
        "budget_implication": budget,
        "decision_maker_involved": dm,
        "days_to_action_window": window,
        "summary": (signal.title or "Signal detected")[:280],
    }


def sanitize_classification(payload: dict, signal: Signal) -> dict:
    """Validate/coerce a model response, falling back per-field to heuristics."""
    fallback = heuristic_classification(signal)
    tier = str(payload.get("urgency_tier", "")).upper()
    budget = str(payload.get("budget_implication", "")).upper()
    try:
        window = int(payload.get("days_to_action_window"))
        if not 1 <= window <= 365:
            raise ValueError
    except (TypeError, ValueError):
        window = fallback["days_to_action_window"]
    summary = str(payload.get("summary") or "").strip() or fallback["summary"]
    return {
        "signal_type": signal.signal_type,
        "urgency_tier": tier if tier in VALID_TIERS else fallback["urgency_tier"],
        "budget_implication": budget if budget in VALID_BUDGET else fallback["budget_implication"],
        "decision_maker_involved": bool(payload.get("decision_maker_involved", fallback["decision_maker_involved"])),
        "days_to_action_window": window,
        "summary": summary[:500],
    }


async def classify_signal(signal: Signal, org_id: Optional[str] = None) -> dict:
    """Classify one signal via Claude Haiku, with heuristic fallback."""
    fallback_json = json.dumps(heuristic_classification(signal))
    prompt = (
        f"Signal source: {signal.source}\n"
        f"Detected signal type hint: {signal.signal_type}\n"
        f"Title: {signal.title}\n"
        f"Raw data: {json.dumps(signal.raw_data or {}, default=str)[:2000]}"
    )
    response = await claude_call(
        model=settings.model_haiku,
        system=SIGNAL_CLASSIFIER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.0,
        org_id=org_id,
        fallback=fallback_json,
    )
    parsed = extract_json(response)
    if parsed is None:
        logger.warning("Classifier: unparseable response for signal %s, using heuristic", signal.id)
        return heuristic_classification(signal)
    return sanitize_classification(parsed, signal)


# --- Pipeline nodes ----------------------------------------------------------


async def _node_load_new(state: dict) -> dict:
    db: AsyncSession = state["db"]
    result = await db.execute(
        select(Signal).where(Signal.status == "new").limit(state.get("batch_size", 50))
    )
    return {"signals": list(result.scalars().all())}


async def _node_classify(state: dict) -> dict:
    org_id = str(state.get("org_id", "")) or None
    classifications = {}
    for signal in state.get("signals", []):
        classifications[signal.id] = await classify_signal(signal, org_id=org_id)
    return {"classifications": classifications}


async def _node_persist(state: dict) -> dict:
    db: AsyncSession = state["db"]
    updated = 0
    for signal in state.get("signals", []):
        payload = state.get("classifications", {}).get(signal.id)
        if payload is None:
            continue
        signal.urgency_tier = payload["urgency_tier"]
        signal.budget_implication = payload["budget_implication"]
        signal.decision_maker_involved = payload["decision_maker_involved"]
        signal.days_to_action_window = payload["days_to_action_window"]
        signal.summary = payload["summary"]
        signal.processed_at = utcnow()
        signal.status = "classified"
        updated += 1
    await db.commit()
    logger.info("Intent Classifier: classified %d signals", updated)
    return {"classified_count": updated}


PIPELINE_NODES = [
    ("load_new", _node_load_new),
    ("classify", _node_classify),
    ("persist", _node_persist),
]


async def run_intent_classifier(org_id: uuid.UUID, db: AsyncSession) -> dict:
    """Classify all pending signals for the pipeline run."""
    pipeline = compile_pipeline("intent_classifier", PIPELINE_NODES)
    return await pipeline.ainvoke({"org_id": org_id, "db": db})
