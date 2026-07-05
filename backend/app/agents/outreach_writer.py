"""AGENT 4 — Outreach Writer.

Generates three outreach variants (assertive / analytical / challenger) per
account via OpenRouter: a mid-tier reasoning model first (Kimi K2 Thinking),
escalating to Claude Opus only if the mid-tier draft fails the quality
gate — see app.core.llm_router. A quality gate rejects drafts that break
the rules (generic openers, >3 sentences, banned phrases, no signal
reference, em dashes) before falling back to a deterministic
signal-referencing template that always passes.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.intent_classifier import extract_json
from app.core import llm_router
from app.core.prompts import (
    OUTREACH_OUTPUT_INSTRUCTIONS,
    OUTREACH_VARIANT_FRAMES,
    OUTREACH_WRITER_SYSTEM_PROMPT,
)
from app.db.models import Account, ActionQueueEntry, ICPProfile, OutreachDraft, Signal

logger = logging.getLogger("nexus.agents.outreach")

VARIANTS = ("assertive", "analytical", "challenger")

BANNED_PHRASES = (
    "hope this finds you well",
    "circling back",
    "touching base",
    "synergy",
    "leverage",
    "value-add",
)

MAX_EMAIL_SENTENCES = 3
MAX_SUBJECT_WORDS = 7


def count_sentences(text: str) -> int:
    """Sentence count via terminal punctuation; robust to abbreviations enough
    for a 3-sentence gate."""
    return len([s for s in re.split(r"[.!?]+", text or "") if s.strip()])


def quality_violations(draft: dict, signal_title: str) -> list[str]:
    """All quality-gate rule violations for a draft dict. Empty list = pass."""
    if draft.get("error") == "quality_gate_fail":
        return [f"model declined: {draft.get('reason', 'no reason given')}"]

    violations: list[str] = []
    body = draft.get("email_body", "") or ""
    subject = draft.get("email_subject", "") or ""
    all_copy = " ".join(
        str(draft.get(key, "") or "")
        for key in ("email_subject", "email_body", "linkedin_message", "call_script")
    )
    lowered = all_copy.lower()

    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            violations.append(f"banned phrase: {phrase}")
    if count_sentences(body) > MAX_EMAIL_SENTENCES:
        violations.append(f"email body exceeds {MAX_EMAIL_SENTENCES} sentences")
    if len(subject.split()) > MAX_SUBJECT_WORDS:
        violations.append(f"subject exceeds {MAX_SUBJECT_WORDS} words")
    if "—" in all_copy or "--" in all_copy:
        violations.append("contains em dash or double hyphen")
    if not body.strip():
        violations.append("empty email body")
    # The body must anchor to the specific signal: require at least one
    # distinctive word (>4 chars) from the signal title.
    anchor_words = [w.lower() for w in re.findall(r"[A-Za-z]{5,}", signal_title or "")]
    if anchor_words and not any(w in lowered for w in anchor_words):
        violations.append("does not reference the specific signal")
    return violations


def template_draft(variant: str, account: Account, signal: Signal, offer: str) -> dict:
    """Deterministic fallback draft that always passes the quality gate.

    Written per the outreach philosophy: signal reference, cost framing,
    small ask, no product pitch, no banned phrases, no em dashes.
    """
    company = account.company_name
    signal_line = (signal.title or signal.summary or "a recent change at your company").strip()
    openers = {
        "assertive": f"Saw that {signal_line}.",
        "analytical": f"One data point stood out this week: {signal_line}.",
        "challenger": f"Most teams misread what follows a moment like this: {signal_line}.",
    }
    return {
        "email_subject": f"Question about {company.split(' ')[0]}'s next 90 days"[:80],
        "email_body": (
            f"{openers.get(variant, openers['analytical'])} "
            f"In my experience the real cost shows up in the 60 to 90 days after, "
            f"while priorities are still unassigned. "
            f"Open to a 15 minute call this week to compare notes?"
        ),
        "linkedin_message": (
            f"Noticed the news at {company}. "
            f"Worth 15 minutes to compare notes on what usually follows?"
        ),
        "call_script": (
            f"Hi, this is about {company}, not a pitch. I track moments like this one: "
            f"{signal_line}. Usually there is a 90 day window before priorities harden. "
            f"Is that window on your radar yet?"
        ),
        "positioning_frame": (
            f"Signal: {signal.signal_type} at {company}. The sender's offer ({offer[:120] or 'B2B services'}) "
            f"maps to the capability gap this signal exposes. First-mover advantage: "
            f"no RFP exists yet, so there is no competitive comparison to lose."
        ),
    }


async def generate_variant(
    variant: str,
    account: Account,
    signal: Signal,
    icp: Optional[ICPProfile],
    org_id: Optional[str],
) -> dict:
    """Generate one variant, gate it, escalate to the premium tier once on
    failure, then fall back to the deterministic template."""
    offer = (icp.offer_description if icp else "") or ""
    fallback_dict = template_draft(variant, account, signal, offer)
    context = (
        f"ACCOUNT: {account.company_name} ({account.industry or 'unknown industry'}, "
        f"{account.employee_count or '?'} employees, {account.geography or 'unknown geo'})\n"
        f"SIGNAL ({signal.signal_type}, tier {signal.urgency_tier or 'unclassified'}): "
        f"{signal.title}\n"
        f"SIGNAL SUMMARY: {signal.summary or 'n/a'}\n"
        f"SENDER'S OFFER: {offer or 'B2B consulting and services'}\n\n"
        f"{OUTREACH_VARIANT_FRAMES[variant]}\n{OUTREACH_OUTPUT_INSTRUCTIONS}"
    )

    def passes_gate(raw_text: str) -> bool:
        parsed = extract_json(raw_text)
        return parsed is not None and not quality_violations(parsed, signal.title or "")

    raw, model_used, fallback_used = await llm_router.generate(
        system=OUTREACH_WRITER_SYSTEM_PROMPT,
        prompt=context,
        org_id=org_id,
        quality_check=passes_gate,
        deterministic_fallback=json.dumps(fallback_dict),
        max_tokens=800,
        temperature=0.7,
    )

    if model_used == "template":
        logger.info("Outreach: using template fallback for %s/%s", account.company_name, variant)
        return fallback_dict

    parsed = extract_json(raw)
    if parsed is None:
        logger.warning(
            "Outreach: %s response unparseable for %s/%s despite passing quality_check, using template",
            model_used, account.company_name, variant,
        )
        return fallback_dict
    if fallback_used:
        logger.info("Outreach: %s (tier 3) used for %s/%s after tier 2 failed", model_used, account.company_name, variant)
    return parsed


async def generate_outreach_for_account(
    account_id: uuid.UUID, db: AsyncSession
) -> list[OutreachDraft]:
    """Generate and persist 3 outreach variants for an account.

    Uses the account's strongest classified signal as the anchor. Marks any
    pending Action Queue entry as ``outreach_generated``.
    """
    account = (
        await db.execute(select(Account).where(Account.id == account_id))
    ).scalars().first()
    if account is None:
        raise ValueError(f"Account {account_id} not found")

    signals = (
        (
            await db.execute(
                select(Signal)
                .where(Signal.account_id == account_id, Signal.status != "archived")
                .order_by(Signal.detected_at.desc())
            )
        )
        .scalars()
        .all()
    )
    if not signals:
        raise ValueError(f"Account {account_id} has no signals to reference")
    # Prefer HOT classified signals, then WARM, then most recent.
    tier_rank = {"HOT": 0, "WARM": 1, "COOL": 2, None: 3}
    anchor = sorted(signals, key=lambda s: tier_rank.get(s.urgency_tier, 3))[0]

    icp = (
        await db.execute(
            select(ICPProfile)
            .where(ICPProfile.org_id == account.org_id)
            .order_by(ICPProfile.created_at.desc())
        )
    ).scalars().first()

    drafts: list[OutreachDraft] = []
    for variant in VARIANTS:
        payload = await generate_variant(
            variant, account, anchor, icp, org_id=str(account.org_id)
        )
        draft = OutreachDraft(
            account_id=account.id,
            variant=variant,
            email_subject=str(payload.get("email_subject", ""))[:255],
            email_body=str(payload.get("email_body", "")),
            linkedin_message=str(payload.get("linkedin_message", "")),
            call_script=str(payload.get("call_script", "")),
            positioning_frame=str(payload.get("positioning_frame", "")),
            signal_reference=(anchor.title or anchor.summary or "")[:2000],
        )
        db.add(draft)
        drafts.append(draft)

    queue_entry = (
        await db.execute(
            select(ActionQueueEntry).where(
                ActionQueueEntry.account_id == account.id,
                ActionQueueEntry.status == "pending",
            )
        )
    ).scalars().first()
    if queue_entry is not None:
        queue_entry.status = "outreach_generated"

    await db.commit()
    return drafts
