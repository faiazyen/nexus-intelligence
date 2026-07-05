"""EXECUTIVE ROUTER — supervisor orchestrating the NEXUS agent pipeline.

Sequences Signal Scout -> Intent Classifier -> Account Scorer with the
org-level cost guardrail checked before every LLM-calling stage. Outreach
Writer and Business Brain are demand-driven (user-triggered), never
scheduled — that is how the $0.50/day/100-account guardrail holds: Haiku
does all classification, Opus runs only on explicit user actions.

Errors from any stage are collected into a human-review list instead of
aborting the run.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.account_scorer import run_account_scorer
from app.agents.intent_classifier import run_intent_classifier
from app.agents.signal_scout import run_signal_scout
from app.core.llm import BudgetExceededError, cost_tracker

logger = logging.getLogger("nexus.agents.supervisor")


async def run_pipeline(org_id: uuid.UUID, db: AsyncSession) -> dict:
    """One full monitor->reason->score cycle for an organization.

    Returns a run summary::

        {
          "persisted_signals": int,
          "classified_signals": int,
          "queued_accounts": int,
          "human_review": [ {stage, error}, ... ],
          "budget_blocked": bool,
        }
    """
    summary = {
        "persisted_signals": 0,
        "classified_signals": 0,
        "queued_accounts": 0,
        "human_review": [],
        "budget_blocked": False,
    }

    # Stage 1 — Signal Scout (no LLM calls; network only).
    try:
        scout_state = await run_signal_scout(org_id, db)
        summary["persisted_signals"] = scout_state.get("persisted_count", 0)
        summary["human_review"].extend(scout_state.get("errors", []))
    except Exception as exc:  # noqa: BLE001 — collect, don't abort
        logger.exception("Supervisor: signal scout failed")
        summary["human_review"].append({"stage": "signal_scout", "error": str(exc)})

    # Stage 2 — Intent Classifier (Haiku; enforce budget first).
    try:
        await cost_tracker.check_budget(str(org_id))
        classifier_state = await run_intent_classifier(org_id, db)
        summary["classified_signals"] = classifier_state.get("classified_count", 0)
        summary["human_review"].extend(classifier_state.get("errors", []))
    except BudgetExceededError as exc:
        logger.warning("Supervisor: budget exceeded before classification: %s", exc)
        summary["budget_blocked"] = True
        summary["human_review"].append({"stage": "intent_classifier", "error": str(exc)})
    except Exception as exc:  # noqa: BLE001
        logger.exception("Supervisor: intent classifier failed")
        summary["human_review"].append({"stage": "intent_classifier", "error": str(exc)})

    # Stage 3 — Account Scorer (pure math; always runs).
    try:
        scorer_state = await run_account_scorer(org_id, db)
        summary["queued_accounts"] = scorer_state.get("queued_count", 0)
        summary["human_review"].extend(scorer_state.get("errors", []))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Supervisor: account scorer failed")
        summary["human_review"].append({"stage": "account_scorer", "error": str(exc)})

    logger.info(
        "Supervisor run for org %s: %d signals, %d classified, %d queued, %d for review",
        org_id,
        summary["persisted_signals"],
        summary["classified_signals"],
        summary["queued_accounts"],
        len(summary["human_review"]),
    )
    return summary
