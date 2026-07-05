"""OpenRouter-routed multi-model LLM interface for NEXUS.

Replaces the old direct-Anthropic wrapper (``app.core.llm``, now unused by
every caller) with a single OpenRouter account routing across cost tiers.
One API key (``OPENROUTER_API_KEY``), one SDK (the standard ``openai``
package pointed at OpenRouter's OpenAI-compatible endpoint) — OpenRouter
does not publish a bespoke Python package with a stable, documented API
surface; the OpenAI-SDK-compatible route is the one their own docs and the
broader ecosystem (Real Python, Snyk, instructor) treat as canonical.

MODEL SLUGS: every one below was checked against OpenRouter's live
``/api/v1/models`` catalog at the time this module was written, not
recalled from training data. OpenRouter's free tier and pricing churn
fast — a slug that isn't re-verified against that endpoint should be
treated as unverified, not assumed correct. As of writing:

  Tier 0 (free, best-effort):
    nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
  Tier 1 (ultra-cheap, paid):
    deepseek/deepseek-v4-flash            (~$0.09 / $0.18 per 1M tokens)
  Tier 2 (mid-tier, quality):
    moonshotai/kimi-k2-thinking           (~$0.60 / $2.50 per 1M tokens)
  Tier 3 (premium fallback):
    anthropic/claude-opus-4.8             (~$5.00 / $25.00 per 1M tokens)

COST ACCOUNTING: OpenRouter returns the authoritative per-request USD cost
inline in every response (``usage.cost``) as of mid-2026 — the
``usage: {include: true}`` opt-in flag some older docs mention is
deprecated and now a no-op; cost is simply always present. This module
reads that field directly rather than maintaining a hardcoded
per-million-token price table, since the table above is already a
snapshot that will drift. A small reference table is kept only as a
last-resort estimate for the rare case the field is ever absent.

Every task has a zero-cost, zero-network final fallback that this module
never overrides: the rule-based heuristic classifier
(``app.agents.intent_classifier.heuristic_classification``) or the
deterministic outreach template (``app.agents.outreach_writer.template_draft``).
Nothing routed through here can fail a caller outright.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Callable, Optional

from app.core.config import settings

logger = logging.getLogger("nexus.llm_router")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
RETRY_DELAYS_SECONDS = (1.0, 2.0, 4.0)

# Last-resort estimate ONLY — used if a response is ever missing the
# authoritative usage.cost field OpenRouter normally provides. Not the
# primary accounting mechanism. USD per million tokens (input, output).
_FALLBACK_PRICING = {
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": (0.0, 0.0),
    "deepseek/deepseek-v4-flash": (0.09, 0.18),
    "moonshotai/kimi-k2-thinking": (0.60, 2.50),
    "anthropic/claude-opus-4.8": (5.00, 25.00),
}
_DEFAULT_FALLBACK_PRICE = (1.0, 5.0)


class LLMUnavailableError(Exception):
    """Raised when OpenRouter cannot be reached after all retries and no
    fallback string was supplied."""


class BudgetExceededError(Exception):
    """Raised when an org has exhausted its daily LLM budget and the caller
    has no cheaper path left to try."""


def _purpose_default_model(purpose: str) -> str:
    return {
        "classify": settings.nexus_llm_classifier,
        "classify_fallback": settings.nexus_llm_classifier_fallback,
        "outreach": settings.nexus_llm_outreach,
        "brain": settings.nexus_llm_brain,
        "fallback": settings.nexus_llm_fallback,
    }[purpose]


@dataclass
class CallRecord:
    """One completed (or demo-mode) LLM call, for cost logging."""

    ts: str
    org_id: str
    model: str
    purpose: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    fallback_used: bool = False
    demo_mode: bool = False


@dataclass
class CostTracker:
    """Per-org daily spend accumulator, backed by an append-only JSONL log.

    No Redis: this is a single-user, single-process dogfood MVP (see
    docs/PRODUCT_AUDIT_AND_MVP.md section F) — a plain file survives
    process restarts and is trivially inspectable, which a distributed
    cache is not.
    """

    daily_limit_usd: float = field(default_factory=lambda: settings.nexus_daily_llm_limit)
    log_path: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "logs" / "llm_cost.jsonl"
    )
    _memory: dict = field(default_factory=dict)

    def _key(self, org_id: str) -> str:
        return f"{org_id}:{date.today().isoformat()}"

    def record(self, rec: CallRecord) -> None:
        key = self._key(rec.org_id)
        self._memory[key] = self._memory.get(key, 0.0) + rec.cost_usd
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec.__dict__) + "\n")
        except OSError as exc:  # noqa: BLE001 — logging cost must never break a call
            logger.warning("CostTracker: failed to write cost log: %s", exc)

    def spent_today(self, org_id: str) -> float:
        return self._memory.get(self._key(org_id), 0.0)

    def is_over_budget(self, org_id: str) -> bool:
        return self.spent_today(org_id) >= self.daily_limit_usd

    async def check_budget(self, org_id: str) -> None:
        """Raise ``BudgetExceededError`` if the org is over its daily limit.

        Used by the supervisor to skip an entire pipeline stage upfront;
        the softer per-call ``is_over_budget`` check inside classify()/
        generate()/brain_call() handles graceful mid-pipeline downgrades
        to free tiers instead of hard-stopping.
        """
        if self.is_over_budget(org_id):
            raise BudgetExceededError(
                f"Org {org_id} has spent ${self.spent_today(org_id):.4f} of its "
                f"${self.daily_limit_usd:.2f} daily LLM budget."
            )

    def today_summary(self, org_id: str) -> dict:
        """Rows logged today for this org, read back from the JSONL file.

        Reading from disk (not memory) so the /costs endpoint reflects
        history across process restarts, not just the current run.
        """
        today = date.today().isoformat()
        rows: list[dict] = []
        if self.log_path.exists():
            with self.log_path.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if row.get("org_id") == org_id and row.get("ts", "").startswith(today):
                        rows.append(row)

        by_model: dict = {}
        by_purpose: dict = {}
        by_purpose_model: dict = {}  # purpose -> {model: cost}, for "which model handled X" in the UI
        fallback_events: list[dict] = []
        total = 0.0
        for row in rows:
            total += row["cost_usd"]
            by_model.setdefault(row["model"], 0.0)
            by_model[row["model"]] += row["cost_usd"]
            by_purpose.setdefault(row["purpose"], 0.0)
            by_purpose[row["purpose"]] += row["cost_usd"]
            by_purpose_model.setdefault(row["purpose"], {}).setdefault(row["model"], 0.0)
            by_purpose_model[row["purpose"]][row["model"]] += row["cost_usd"]
            if row.get("fallback_used"):
                fallback_events.append(row)

        # For each purpose, the model that handled the most spend today —
        # a single representative label for a compact UI summary line.
        top_model_by_purpose = {
            purpose: max(models, key=models.get)
            for purpose, models in by_purpose_model.items()
            if models
        }
        return {
            "total_usd": round(total, 6),
            "by_model": {k: round(v, 6) for k, v in by_model.items()},
            "by_purpose": {k: round(v, 6) for k, v in by_purpose.items()},
            "top_model_by_purpose": top_model_by_purpose,
            "fallback_events": fallback_events,
            "daily_limit_usd": self.daily_limit_usd,
            "over_budget": total >= self.daily_limit_usd,
        }


cost_tracker = CostTracker()

_DEMO_FALLBACK = (
    "[NEXUS demo mode] No OPENROUTER_API_KEY is configured, so this is a "
    "canned response. Add your key to .env to enable live intelligence."
)


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_price, out_price = _FALLBACK_PRICING.get(model, _DEFAULT_FALLBACK_PRICE)
    return (input_tokens * in_price + output_tokens * out_price) / 1_000_000


def _extract_cost(response, model: str, input_tokens: int, output_tokens: int) -> float:
    """Prefer OpenRouter's authoritative usage.cost; estimate only if absent."""
    usage = getattr(response, "usage", None)
    cost = getattr(usage, "cost", None)
    if cost is None and usage is not None:
        extra = getattr(usage, "model_extra", None) or {}
        cost = extra.get("cost")
    if cost is None:
        logger.info("llm_router: usage.cost missing for %s, using estimate", model)
        return _estimate_cost(model, input_tokens, output_tokens)
    return float(cost)


def _get_client():
    from openai import AsyncOpenAI

    return AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key)


async def _call(
    *,
    model: str,
    system: str,
    prompt: str,
    purpose: str,
    org_id: Optional[str],
    max_tokens: int,
    temperature: float,
    fallback: Optional[str],
    fallback_used: bool = False,
) -> str:
    """One non-streaming OpenRouter call with retries and cost logging.

    Demo mode (no key) returns ``fallback`` immediately, exactly like the
    old direct-Anthropic wrapper, so the whole platform still runs without
    credentials.
    """
    if not settings.openrouter_api_key:
        logger.info("llm_router: no API key, demo fallback (model=%s, purpose=%s)", model, purpose)
        if org_id is not None:
            cost_tracker.record(
                CallRecord(
                    ts=datetime.now(timezone.utc).isoformat(),
                    org_id=org_id, model=model, purpose=purpose,
                    tokens_in=0, tokens_out=0, cost_usd=0.0,
                    fallback_used=fallback_used, demo_mode=True,
                )
            )
        return fallback if fallback is not None else _DEMO_FALLBACK

    last_error: Optional[Exception] = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS, start=1):
        try:
            client = _get_client()
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "prompt_tokens", 0) or 0
            output_tokens = getattr(usage, "completion_tokens", 0) or 0
            cost = _extract_cost(response, model, input_tokens, output_tokens)
            logger.info(
                "llm_router model=%s purpose=%s in=%d out=%d cost_usd=%.6f org=%s fallback=%s",
                model, purpose, input_tokens, output_tokens, cost, org_id, fallback_used,
            )
            if org_id is not None:
                cost_tracker.record(
                    CallRecord(
                        ts=datetime.now(timezone.utc).isoformat(),
                        org_id=org_id, model=model, purpose=purpose,
                        tokens_in=input_tokens, tokens_out=output_tokens,
                        cost_usd=cost, fallback_used=fallback_used,
                    )
                )
            return response.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001 — classify below
            last_error = exc
            logger.warning(
                "llm_router attempt %d/%d failed (model=%s, %s); retrying in %.0fs",
                attempt, len(RETRY_DELAYS_SECONDS), model, exc, delay,
            )
            await asyncio.sleep(delay)

    if fallback is not None:
        logger.error("llm_router: all retries failed for %s, using fallback: %s", model, last_error)
        return fallback
    raise LLMUnavailableError(f"OpenRouter unavailable after retries ({model}): {last_error}")


async def _call_stream(
    *,
    model: str,
    system: str,
    prompt: str,
    purpose: str,
    org_id: Optional[str],
    max_tokens: int,
    temperature: float,
    fallback: Optional[str],
) -> AsyncIterator[str]:
    """Streaming variant of ``_call``. Demo mode streams word-by-word."""
    if not settings.openrouter_api_key:
        text = fallback if fallback is not None else _DEMO_FALLBACK
        for word in text.split(" "):
            yield word + " "
            await asyncio.sleep(0.02)
        return

    last_error: Optional[Exception] = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS, start=1):
        output_text = ""
        try:
            client = _get_client()
            stream = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    output_text += delta
                    yield delta
            # Streaming chunks don't carry usage.cost; estimate from the
            # accumulated text (~4 chars/token, input unknown here).
            approx_out_tokens = max(1, len(output_text) // 4)
            cost = _estimate_cost(model, 0, approx_out_tokens)
            if org_id is not None:
                cost_tracker.record(
                    CallRecord(
                        ts=datetime.now(timezone.utc).isoformat(),
                        org_id=org_id, model=model, purpose=purpose,
                        tokens_in=0, tokens_out=approx_out_tokens, cost_usd=cost,
                    )
                )
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if output_text:
                # Some text already reached the caller (and, for brain_chat,
                # the user's screen). Retrying now would restart the model
                # from scratch and yield a second, duplicate copy on top of
                # what's already rendered — worse than just ending cleanly.
                logger.warning(
                    "llm_router stream failed mid-output (model=%s, %s); "
                    "ending stream instead of retrying to avoid duplicate output",
                    model, exc,
                )
                return
            logger.warning(
                "llm_router stream attempt %d/%d failed before any output (model=%s, %s); retrying in %.0fs",
                attempt, len(RETRY_DELAYS_SECONDS), model, exc, delay,
            )
            await asyncio.sleep(delay)

    # Mirror _call's contract exactly: a fallback provided by the caller is
    # a deliberate "degrade gracefully right here" instruction, so yield it.
    # No fallback means the caller (e.g. brain_stream escalating tier2 ->
    # tier3) wants to know this tier is genuinely exhausted — raise so its
    # try/except can act, rather than silently yielding generic demo text
    # and never attempting the next tier at all.
    if fallback is not None:
        logger.error("llm_router: all stream retries failed for %s, using fallback: %s", model, last_error)
        for word in fallback.split(" "):
            yield word + " "
        return
    raise LLMUnavailableError(f"OpenRouter stream unavailable after retries ({model}): {last_error}")


# --- Public routing API ------------------------------------------------------


async def classify(
    *,
    system: str,
    prompt: str,
    org_id: Optional[str],
    heuristic_fallback: str,
    max_tokens: int = 400,
) -> str:
    """Route a classification task: Tier 0 (free) -> Tier 1 (cheap) ->
    the caller's rule-based heuristic (zero-cost, always available).

    Both tiers are non-Claude models, so they share the same JSON-strict
    system prompt — there's no reason for them to differ.

    Returns the raw model text (or the heuristic JSON string) for the
    caller to parse — this module doesn't know the classifier's schema.
    """
    if org_id is not None and cost_tracker.is_over_budget(org_id):
        logger.info("llm_router: org %s over budget, skipping straight to heuristic", org_id)
        return heuristic_fallback

    tier0 = settings.nexus_llm_classifier
    try:
        result = await _call(
            model=tier0, system=system, prompt=prompt, purpose="classify",
            org_id=org_id, max_tokens=max_tokens, temperature=0.1,
            fallback=None,
        )
        if result.strip():
            return result
    except Exception as exc:  # noqa: BLE001 — free tier is best-effort only
        logger.info("llm_router: tier0 classify failed (%s), falling back to tier1", exc)

    tier1 = settings.nexus_llm_classifier_fallback
    return await _call(
        model=tier1, system=system, prompt=prompt, purpose="classify_fallback",
        org_id=org_id, max_tokens=max_tokens, temperature=0.1,
        fallback=heuristic_fallback, fallback_used=True,
    )


async def generate(
    *,
    system: str,
    prompt: str,
    org_id: Optional[str],
    quality_check: Callable[[str], bool],
    deterministic_fallback: str,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> tuple[str, str, bool]:
    """Route a generation task (outreach): Tier 2 -> Tier 3 (only if Tier 2
    fails ``quality_check``) -> the caller's deterministic template.

    ``quality_check`` takes the raw model text and returns True/False.
    Returns ``(text, model_used, fallback_used)``.
    """
    if org_id is not None and cost_tracker.is_over_budget(org_id):
        logger.info("llm_router: org %s over budget, skipping to template", org_id)
        return deterministic_fallback, "template", True

    if settings.nexus_disable_claude:
        tier2 = settings.nexus_llm_outreach
        result = await _call(
            model=tier2, system=system, prompt=prompt, purpose="outreach",
            org_id=org_id, max_tokens=max_tokens, temperature=temperature,
            fallback=deterministic_fallback,
        )
        if quality_check(result):
            return result, tier2, False
        return deterministic_fallback, "template", True

    tier2 = settings.nexus_llm_outreach
    try:
        result = await _call(
            model=tier2, system=system, prompt=prompt, purpose="outreach",
            org_id=org_id, max_tokens=max_tokens, temperature=temperature,
            fallback=None,
        )
        if quality_check(result):
            return result, tier2, False
    except Exception as exc:  # noqa: BLE001
        logger.info("llm_router: tier2 outreach failed (%s), trying tier3", exc)

    tier3 = settings.nexus_llm_fallback
    try:
        result = await _call(
            model=tier3, system=system, prompt=prompt, purpose="outreach_fallback",
            org_id=org_id, max_tokens=max_tokens, temperature=temperature,
            fallback=None, fallback_used=True,
        )
        if quality_check(result):
            return result, tier3, True
    except Exception as exc:  # noqa: BLE001
        logger.info("llm_router: tier3 outreach also failed (%s), using template", exc)

    return deterministic_fallback, "template", True


async def brain_call(
    *, system: str, prompt: str, org_id: Optional[str], fallback: str, max_tokens: int = 1200,
) -> str:
    """Route a non-streaming Brain task (briefing, coaching): Tier 2 ->
    Tier 3 on failure -> the caller's demo-mode fallback text."""
    if org_id is not None and cost_tracker.is_over_budget(org_id):
        return fallback

    tier2 = settings.nexus_llm_brain
    try:
        return await _call(
            model=tier2, system=system, prompt=prompt, purpose="brain",
            org_id=org_id, max_tokens=max_tokens, temperature=0.4,
            fallback=None,
        )
    except Exception as exc:  # noqa: BLE001
        logger.info("llm_router: tier2 brain failed (%s), trying tier3", exc)

    if settings.nexus_disable_claude:
        return fallback
    tier3 = settings.nexus_llm_fallback
    return await _call(
        model=tier3, system=system, prompt=prompt, purpose="brain_fallback",
        org_id=org_id, max_tokens=max_tokens, temperature=0.4,
        fallback=fallback, fallback_used=True,
    )


async def brain_stream(
    *, system: str, prompt: str, org_id: Optional[str], fallback: str, max_tokens: int = 2048,
) -> AsyncIterator[str]:
    """Streaming Brain task. Falls back to Tier 3 only if Tier 2 errors
    before yielding anything; once streaming has started, a mid-stream
    failure just ends the stream rather than switching models underneath
    a partially-rendered answer."""
    if org_id is not None and cost_tracker.is_over_budget(org_id):
        for word in fallback.split(" "):
            yield word + " "
            await asyncio.sleep(0.02)
        return

    tier2 = settings.nexus_llm_brain
    tier3 = settings.nexus_llm_fallback if not settings.nexus_disable_claude else None
    try:
        async for chunk in _call_stream(
            model=tier2, system=system, prompt=prompt, purpose="brain",
            org_id=org_id, max_tokens=max_tokens, temperature=0.4, fallback=None,
        ):
            yield chunk
        return
    except Exception as exc:  # noqa: BLE001
        logger.info("llm_router: tier2 brain stream failed (%s)", exc)

    if tier3:
        async for chunk in _call_stream(
            model=tier3, system=system, prompt=prompt, purpose="brain_fallback",
            org_id=org_id, max_tokens=max_tokens, temperature=0.4, fallback=fallback,
        ):
            yield chunk
    else:
        for word in fallback.split(" "):
            yield word + " "
            await asyncio.sleep(0.02)
