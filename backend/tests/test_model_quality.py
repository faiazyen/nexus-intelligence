"""Manual model-quality comparison harness (Fix 10, item g).

Runs the same classify/outreach/brain input through the free tier, the
mid tier, and the premium (Claude) tier, side by side, and writes the
outputs to a JSON file for a human to read and judge. This deliberately
does NOT assert anything about which model is "better" — that's a
product judgment call a human makes by reading real output, not
something a pytest assertion should decide.

Skips entirely (not a failure) when OPENROUTER_API_KEY isn't set, since
it makes real, billed API calls — it must never run in CI by accident
and must never be mistaken for a correctness test. Run explicitly:

    OPENROUTER_API_KEY=... pytest tests/test_model_quality.py -v -s
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.core.config import settings

pytestmark = pytest.mark.skipif(
    not settings.openrouter_api_key,
    reason="Requires a real OPENROUTER_API_KEY; makes real, billed API calls.",
)

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "logs" / "model_quality_comparison.json"

SAMPLE_SIGNAL_TITLE = "Meridian Health names ex-Epic executive Sarah Lindqvist as CIO"
SAMPLE_SIGNAL_RAW = {
    "demo": True,
    "source_detail": "New CIO hire, healthtech, 850 employees, United States",
}


def _write_comparison(task: str, results: dict) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if OUTPUT_PATH.exists():
        try:
            existing = json.loads(OUTPUT_PATH.read_text())
        except json.JSONDecodeError:
            existing = {}
    existing[task] = {
        "compared_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    OUTPUT_PATH.write_text(json.dumps(existing, indent=2))


@pytest.mark.asyncio
async def test_compare_classification_models():
    """Tier 0 (free) vs Tier 1 (cheap) vs Tier 3 (Claude) on one signal."""
    from app.core import llm_router
    from app.core.prompts import SIGNAL_CLASSIFIER_SYSTEM_PROMPT_STRICT

    prompt = (
        f"Signal source: newsapi\n"
        f"Detected signal type hint: leadership_change\n"
        f"Title: {SAMPLE_SIGNAL_TITLE}\n"
        f"Raw data: {json.dumps(SAMPLE_SIGNAL_RAW)}"
    )
    results = {}
    for label, model in (
        ("tier0_free", settings.nexus_llm_classifier),
        ("tier1_cheap", settings.nexus_llm_classifier_fallback),
        ("tier3_claude", settings.nexus_llm_fallback),
    ):
        text = await llm_router._call(  # noqa: SLF001 — intentional direct tier probe for comparison
            model=model,
            system=SIGNAL_CLASSIFIER_SYSTEM_PROMPT_STRICT,
            prompt=prompt,
            purpose="classify",
            org_id=f"model-quality-test-{uuid.uuid4()}",
            max_tokens=400,
            temperature=0.1,
            fallback=None,
        )
        results[label] = {"model": model, "output": text}

    _write_comparison("classification", results)
    print(f"\nClassification comparison written to {OUTPUT_PATH}")


@pytest.mark.asyncio
async def test_compare_outreach_models():
    """Tier 2 (Kimi) vs Tier 3 (Claude) on the same outreach prompt."""
    from app.core import llm_router
    from app.core.prompts import (
        OUTREACH_OUTPUT_INSTRUCTIONS,
        OUTREACH_VARIANT_FRAMES,
        OUTREACH_WRITER_SYSTEM_PROMPT,
    )

    context = (
        "ACCOUNT: Meridian Health Systems (healthtech, 850 employees, United States)\n"
        f"SIGNAL (leadership_change, tier HOT): {SAMPLE_SIGNAL_TITLE}\n"
        "SIGNAL SUMMARY: New CIO hire signals a technology vendor review.\n"
        "SENDER'S OFFER: B2B operations transformation consulting.\n\n"
        f"{OUTREACH_VARIANT_FRAMES['analytical']}\n{OUTREACH_OUTPUT_INSTRUCTIONS}"
    )
    results = {}
    for label, model in (
        ("tier2_kimi", settings.nexus_llm_outreach),
        ("tier3_claude", settings.nexus_llm_fallback),
    ):
        text = await llm_router._call(  # noqa: SLF001
            model=model,
            system=OUTREACH_WRITER_SYSTEM_PROMPT,
            prompt=context,
            purpose="outreach",
            org_id=f"model-quality-test-{uuid.uuid4()}",
            max_tokens=800,
            temperature=0.7,
            fallback=None,
        )
        results[label] = {"model": model, "output": text}

    _write_comparison("outreach", results)
    print(f"\nOutreach comparison written to {OUTPUT_PATH}")


@pytest.mark.asyncio
async def test_compare_brain_models():
    """Tier 2 (Kimi) vs Tier 3 (Claude) on the same Brain question."""
    from app.core import llm_router
    from app.core.prompts import BRAIN_SYSTEM_PROMPT

    prompt = (
        "LIVE MARKET SNAPSHOT:\nTOP ACCOUNTS BY NEXUS SCORE:\n"
        "- Meridian Health Systems (healthtech): NEXUS 87\n\n"
        "QUESTION: Who should I call today and why?"
    )
    results = {}
    for label, model in (
        ("tier2_kimi", settings.nexus_llm_brain),
        ("tier3_claude", settings.nexus_llm_fallback),
    ):
        text = await llm_router._call(  # noqa: SLF001
            model=model,
            system=BRAIN_SYSTEM_PROMPT,
            prompt=prompt,
            purpose="brain",
            org_id=f"model-quality-test-{uuid.uuid4()}",
            max_tokens=1200,
            temperature=0.4,
            fallback=None,
        )
        results[label] = {"model": model, "output": text}

    _write_comparison("brain", results)
    print(f"\nBrain comparison written to {OUTPUT_PATH}")
