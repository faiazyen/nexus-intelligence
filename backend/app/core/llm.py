"""Anthropic client wrapper for every LLM call in NEXUS.

All agents call ``claude_call`` / ``claude_stream`` — never the SDK directly.
Provides: retry with exponential backoff (1s/2s/4s), token + cost logging,
a per-org daily cost guardrail, and deterministic demo fallbacks so the whole
platform runs without an ``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import AsyncIterator, Optional

from app.core.config import settings

logger = logging.getLogger("nexus.llm")

RETRY_DELAYS_SECONDS = (1.0, 2.0, 4.0)

# USD per million tokens (input, output) per model tier — for cost logging
# and the daily budget guardrail. Approximate; update alongside pricing.
_TIER_PRICES = {
    "opus": (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku": (0.80, 4.0),
}


class LLMUnavailableError(Exception):
    """Raised when the Anthropic API cannot be reached after all retries."""


class BudgetExceededError(Exception):
    """Raised when an org has exhausted its daily LLM budget."""


def _price_for(model: str) -> tuple:
    for tier, prices in _TIER_PRICES.items():
        if tier in model:
            return prices
    return _TIER_PRICES["sonnet"]


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimated USD cost of one call, from per-tier per-million-token prices."""
    in_price, out_price = _price_for(model)
    return (input_tokens * in_price + output_tokens * out_price) / 1_000_000


class CostTracker:
    """Per-org daily LLM spend accumulator with budget enforcement.

    Uses Redis when reachable (key ``nexus:llm_cost:{org}:{date}``, 2-day TTL)
    so the guardrail survives restarts and works across workers; falls back to
    an in-process dict otherwise.
    """

    def __init__(self, daily_budget_usd: Optional[float] = None) -> None:
        self.daily_budget_usd = (
            daily_budget_usd
            if daily_budget_usd is not None
            else settings.daily_llm_budget_usd
        )
        self._memory: dict = {}
        self._redis = None
        self._redis_checked = False

    def _key(self, org_id: str) -> str:
        return f"nexus:llm_cost:{org_id}:{date.today().isoformat()}"

    async def _get_redis(self):
        if self._redis_checked:
            return self._redis
        self._redis_checked = True
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(settings.redis_url, socket_connect_timeout=1)
            await client.ping()
            self._redis = client
        except Exception:  # noqa: BLE001 — any failure means "use memory"
            logger.info("CostTracker: redis unavailable, using in-memory spend tracking")
            self._redis = None
        return self._redis

    async def spent_today(self, org_id: str) -> float:
        """Total USD recorded for this org today."""
        r = await self._get_redis()
        if r is not None:
            try:
                value = await r.get(self._key(org_id))
                return float(value) if value else 0.0
            except Exception:  # noqa: BLE001
                pass
        return self._memory.get(self._key(org_id), 0.0)

    async def record(self, org_id: str, cost_usd: float) -> None:
        """Add a call's cost to today's total."""
        r = await self._get_redis()
        if r is not None:
            try:
                key = self._key(org_id)
                await r.incrbyfloat(key, cost_usd)
                await r.expire(key, 172800)
                return
            except Exception:  # noqa: BLE001
                pass
        key = self._key(org_id)
        self._memory[key] = self._memory.get(key, 0.0) + cost_usd

    async def check_budget(self, org_id: str) -> None:
        """Raise ``BudgetExceededError`` if the org is over its daily budget."""
        spent = await self.spent_today(org_id)
        if spent >= self.daily_budget_usd:
            raise BudgetExceededError(
                f"Org {org_id} has spent ${spent:.4f} of its "
                f"${self.daily_budget_usd:.2f} daily LLM budget."
            )


cost_tracker = CostTracker()

_DEFAULT_FALLBACK = (
    "[NEXUS demo mode] No ANTHROPIC_API_KEY is configured, so this is a "
    "canned response. Add your key to .env to enable live intelligence."
)


def _get_client():
    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=settings.anthropic_api_key)


async def claude_call(
    *,
    model: str,
    system: str,
    messages: list[dict],
    max_tokens: int = 1024,
    temperature: float = 0.3,
    org_id: Optional[str] = None,
    fallback: Optional[str] = None,
) -> str:
    """One non-streaming Claude call with retries, cost logging, and fallback.

    Retries transient failures 3 times (1s/2s/4s). When no API key is set,
    returns ``fallback`` (or a labeled demo string) instead of raising, so
    the platform demos end to end without credentials. Raises
    ``LLMUnavailableError`` only when a key exists but all attempts fail and
    no fallback was provided.
    """
    if not settings.anthropic_api_key:
        logger.info("claude_call: no API key, returning demo fallback (model=%s)", model)
        return fallback if fallback is not None else _DEFAULT_FALLBACK

    if org_id is not None:
        await cost_tracker.check_budget(org_id)

    last_error: Optional[Exception] = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS, start=1):
        try:
            client = _get_client()
            response = await client.messages.create(
                model=model,
                system=system,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "input_tokens", 0) or 0
            output_tokens = getattr(usage, "output_tokens", 0) or 0
            cost = estimate_cost_usd(model, input_tokens, output_tokens)
            logger.info(
                "claude_call model=%s in_tokens=%d out_tokens=%d cost_usd=%.6f org=%s",
                model, input_tokens, output_tokens, cost, org_id,
            )
            if org_id is not None:
                await cost_tracker.record(org_id, cost)
            parts = [block.text for block in response.content if getattr(block, "text", None)]
            return "".join(parts)
        except Exception as exc:  # noqa: BLE001 — classify below
            last_error = exc
            logger.warning(
                "claude_call attempt %d/%d failed (%s); retrying in %.0fs",
                attempt, len(RETRY_DELAYS_SECONDS), exc, delay,
            )
            await asyncio.sleep(delay)

    if fallback is not None:
        logger.error("claude_call: all retries failed, using fallback: %s", last_error)
        return fallback
    raise LLMUnavailableError(f"Anthropic API unavailable after retries: {last_error}")


async def claude_stream(
    *,
    model: str,
    system: str,
    messages: list[dict],
    max_tokens: int = 2048,
    temperature: float = 0.3,
    org_id: Optional[str] = None,
    fallback: Optional[str] = None,
) -> AsyncIterator[str]:
    """Streaming Claude call yielding text deltas, same guarantees as claude_call.

    In demo mode (no API key) the fallback string is yielded in word chunks
    with small delays so streaming UIs behave realistically.
    """
    if not settings.anthropic_api_key:
        text = fallback if fallback is not None else _DEFAULT_FALLBACK
        for word in text.split(" "):
            yield word + " "
            await asyncio.sleep(0.02)
        return

    if org_id is not None:
        await cost_tracker.check_budget(org_id)

    last_error: Optional[Exception] = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS, start=1):
        try:
            client = _get_client()
            output_chars = 0
            async with client.messages.stream(
                model=model,
                system=system,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            ) as stream:
                async for text in stream.text_stream:
                    output_chars += len(text)
                    yield text
            # Rough cost record: ~4 chars/token for output; input unknown here.
            approx_out_tokens = max(1, output_chars // 4)
            cost = estimate_cost_usd(model, 0, approx_out_tokens)
            logger.info(
                "claude_stream model=%s approx_out_tokens=%d cost_usd=%.6f org=%s",
                model, approx_out_tokens, cost, org_id,
            )
            if org_id is not None:
                await cost_tracker.record(org_id, cost)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "claude_stream attempt %d/%d failed (%s); retrying in %.0fs",
                attempt, len(RETRY_DELAYS_SECONDS), exc, delay,
            )
            await asyncio.sleep(delay)

    if fallback is not None:
        for word in fallback.split(" "):
            yield word + " "
        return
    raise LLMUnavailableError(f"Anthropic API unavailable after retries: {last_error}")
