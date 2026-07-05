"""AGENT 5 — Business Brain.

RAG-grounded strategic advisor. Retrieves the org's ingested business
context documents, joins them with live account scores and signals, and
answers via Claude Opus with the verbatim Brain prompt (streaming) —
plus scheduled daily briefings and per-deal coaching.

Retrieval: a dependency-free keyword retriever over ``BusinessContextDoc``
rows. It scores documents by query-term overlap with length normalization —
adequate at MVP document volumes (tens to hundreds of docs per org) and
requiring no embedding service. The upgrade path is Qdrant (settings.qdrant_url)
with an embedding model; swap ``retrieve_context`` only.
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import AsyncIterator, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.llm import claude_call, claude_stream
from app.core.prompts import (
    BRAIN_SYSTEM_PROMPT,
    BRIEFING_SYSTEM_PROMPT,
    DEAL_COACH_SYSTEM_PROMPT,
)
from app.db.models import (
    Account,
    AccountScore,
    ActionQueueEntry,
    BrainBriefing,
    BusinessContextDoc,
    OutreachDraft,
    Signal,
    utcnow,
)

logger = logging.getLogger("nexus.agents.brain")

_STOPWORDS = frozenset(
    "the a an and or of to in for on with is are was were be been what who how why "
    "when where should would could do does did my our your their this that".split()
)


def _terms(text: str) -> list[str]:
    """Lowercased content words (stopwords removed) from free text."""
    return [
        w for w in re.findall(r"[a-z0-9]{3,}", (text or "").lower())
        if w not in _STOPWORDS
    ]


def rank_documents(
    docs: Sequence[BusinessContextDoc], question: str, k: int = 4
) -> list[BusinessContextDoc]:
    """Top-k docs by query-term overlap, normalized by document length."""
    query_terms = set(_terms(question))
    if not query_terms:
        return list(docs[:k])
    scored = []
    for doc in docs:
        doc_terms = _terms(f"{doc.title} {doc.content}")
        if not doc_terms:
            continue
        overlap = sum(1 for t in doc_terms if t in query_terms)
        score = overlap / (1.0 + len(doc_terms) ** 0.5)
        if overlap > 0:
            scored.append((score, doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:k]]


async def retrieve_context(
    db: AsyncSession, org_id: uuid.UUID, question: str, k: int = 4
) -> list[BusinessContextDoc]:
    """Retrieve the org's most relevant business-context documents."""
    docs = (
        (
            await db.execute(
                select(BusinessContextDoc).where(BusinessContextDoc.org_id == org_id)
            )
        )
        .scalars()
        .all()
    )
    return rank_documents(docs, question, k)


async def _market_snapshot(db: AsyncSession, org_id: uuid.UUID, limit: int = 8) -> str:
    """Compact text block of the org's hottest accounts and newest signals."""
    scores = (
        (
            await db.execute(
                select(AccountScore, Account)
                .join(Account, AccountScore.account_id == Account.id)
                .where(Account.org_id == org_id)
                .order_by(AccountScore.scored_at.desc())
                .limit(50)
            )
        )
        .all()
    )
    latest: dict = {}
    for score, account in scores:
        if account.id not in latest:
            latest[account.id] = (score, account)
    top = sorted(latest.values(), key=lambda p: p[0].composite_nexus_score, reverse=True)[:limit]

    lines = ["TOP ACCOUNTS BY NEXUS SCORE:"]
    for score, account in top:
        lines.append(
            f"- {account.company_name} ({account.industry or '?'}): NEXUS {score.composite_nexus_score} "
            f"(urgency {score.urgency}, fit {score.fit}, budget {score.budget_probability})"
        )
    if len(lines) == 1:
        lines.append("- (no scored accounts yet)")

    signals = (
        (
            await db.execute(
                select(Signal)
                .join(Account, Signal.account_id == Account.id)
                .where(Account.org_id == org_id)
                .order_by(Signal.detected_at.desc())
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )
    lines.append("NEWEST SIGNALS:")
    for signal in signals:
        lines.append(
            f"- [{signal.signal_type}/{signal.urgency_tier or 'new'}] {signal.title[:160]}"
        )
    if signals == []:
        lines.append("- (no signals yet)")
    return "\n".join(lines)


def _demo_answer(question: str, snapshot: str) -> str:
    """Grounded fallback answer assembled from live data (demo mode)."""
    return (
        "**NEXUS Brain (demo mode, no API key configured)**\n\n"
        f"You asked: *{question.strip()}*\n\n"
        "Here is what the signal data says right now:\n\n"
        f"{snapshot}\n\n"
        "**Recommended next step:** open the Action Queue and start with the "
        "highest NEXUS Score. Add your ANTHROPIC_API_KEY to get full strategic reasoning."
    )


async def ask(
    org_id: uuid.UUID, question: str, db: AsyncSession
) -> AsyncIterator[str]:
    """Stream a Brain answer grounded in RAG context + live market snapshot."""
    docs = await retrieve_context(db, org_id, question)
    snapshot = await _market_snapshot(db, org_id)
    context_block = "\n\n".join(
        f"[{doc.doc_type}] {doc.title}\n{doc.content[:2000]}" for doc in docs
    ) or "(no business context ingested yet)"

    user_message = (
        f"BUSINESS CONTEXT (from the user's ingested documents):\n{context_block}\n\n"
        f"LIVE MARKET SNAPSHOT:\n{snapshot}\n\n"
        f"QUESTION: {question}"
    )
    async for chunk in claude_stream(
        model=settings.model_opus,
        system=BRAIN_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=2048,
        org_id=str(org_id),
        fallback=_demo_answer(question, snapshot),
    ):
        yield chunk


async def generate_briefing(org_id: uuid.UUID, db: AsyncSession) -> BrainBriefing:
    """Generate and persist today's daily briefing (idempotent per day)."""
    today = utcnow().date()
    existing = (
        await db.execute(
            select(BrainBriefing).where(
                BrainBriefing.org_id == org_id,
                BrainBriefing.briefing_date == today,
            )
        )
    ).scalars().first()
    if existing is not None:
        return existing

    snapshot = await _market_snapshot(db, org_id)
    fallback_md = (
        f"# Daily Brief, {today.isoformat()}\n\n"
        f"## Where the heat is\n\n{snapshot}\n\n"
        "## Recommended actions today\n\n"
        "1. Work the Action Queue from the top score down.\n"
        "2. Generate outreach for any account with 2+ concurrent signals.\n"
        "3. Add business context docs in Settings so briefings get sharper.\n"
    )
    content = await claude_call(
        model=settings.model_opus,
        system=BRIEFING_SYSTEM_PROMPT.replace("{date}", today.isoformat()),
        messages=[{"role": "user", "content": f"LIVE MARKET SNAPSHOT:\n{snapshot}"}],
        max_tokens=1200,
        org_id=str(org_id),
        fallback=fallback_md,
    )
    briefing = BrainBriefing(org_id=org_id, briefing_date=today, content_markdown=content)
    db.add(briefing)
    await db.commit()
    return briefing


async def coach(entry_id: uuid.UUID, db: AsyncSession) -> str:
    """Deal coaching for one Action Queue entry."""
    entry = (
        await db.execute(select(ActionQueueEntry).where(ActionQueueEntry.id == entry_id))
    ).scalars().first()
    if entry is None:
        raise ValueError(f"Action queue entry {entry_id} not found")

    account: Optional[Account] = (
        await db.execute(select(Account).where(Account.id == entry.account_id))
    ).scalars().first()
    signals = (
        (
            await db.execute(
                select(Signal)
                .where(Signal.account_id == entry.account_id)
                .order_by(Signal.detected_at.desc())
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
                .where(OutreachDraft.account_id == entry.account_id)
                .order_by(OutreachDraft.created_at.desc())
                .limit(3)
            )
        )
        .scalars()
        .all()
    )

    name = account.company_name if account else "this account"
    signal_lines = "\n".join(
        f"- [{s.signal_type}/{s.urgency_tier or 'new'}] {s.title}" for s in signals
    ) or "- none"
    outreach_lines = "\n".join(
        f"- {d.variant}: sent={'yes' if d.sent_at else 'no'}, outcome={d.outcome or 'pending'}"
        for d in drafts
    ) or "- no outreach generated yet"

    deal_context = (
        f"ACCOUNT: {name}\nNEXUS SCORE: {entry.nexus_score}\n"
        f"DAYS LEFT IN WINDOW: {entry.days_in_window_estimate}\n"
        f"QUEUE STATUS: {entry.status}\nSIGNALS:\n{signal_lines}\n"
        f"OUTREACH SO FAR:\n{outreach_lines}"
    )
    fallback = (
        f"**Deal stand:** {name} scores NEXUS {entry.nexus_score} with about "
        f"{entry.days_in_window_estimate} days left in the buying window.\n\n"
        f"**Biggest risk:** the window closes while outreach sits ungenerated or unsent.\n\n"
        f"**Do this week:** send the analytical variant first, then follow up on day 4 "
        f"referencing the strongest signal directly."
    )
    return await claude_call(
        model=settings.model_opus,
        system=DEAL_COACH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": deal_context}],
        max_tokens=800,
        org_id=str(account.org_id) if account else None,
        fallback=fallback,
    )
