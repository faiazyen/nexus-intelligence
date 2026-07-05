"""AGENT 1 — Signal Scout.

Collects raw buying signals from external sources every 6 hours (scheduled
by Celery beat in production; callable on demand via the supervisor).

Pipeline: collect -> normalize -> dedupe -> persist.

Each collector degrades gracefully: real HTTP calls where a free API exists
(SEC EDGAR) or an API key is configured (NewsAPI, Crunchbase); realistic
synthetic demo signals otherwise, flagged ``raw_data["demo"] = True`` so the
UI can label them.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import compile_pipeline
from app.core.config import settings
from app.db.models import Account, Signal

logger = logging.getLogger("nexus.agents.scout")

EDGAR_RECENT_FILINGS_URL = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcompany&type=8-K&dateb=&owner=include&count=10&output=atom"
)
EDGAR_USER_AGENT = "NEXUS Intelligence research@nexusintelligence.app"


async def collect_sec_edgar() -> list[dict]:
    """Recent 8-K filings from SEC EDGAR (free, official, no key needed).

    8-K = material corporate events: leadership changes, M&A, restructuring —
    prime pre-RFP triggers. Returns [] on any network failure.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                EDGAR_RECENT_FILINGS_URL, headers={"User-Agent": EDGAR_USER_AGENT}
            )
            response.raise_for_status()
        raw: list[dict] = []
        # Minimal atom parsing without extra deps: split on <entry> blocks.
        for block in response.text.split("<entry>")[1:]:
            title = _between(block, "<title>", "</title>")
            updated = _between(block, "<updated>", "</updated>")
            if not title:
                continue
            company = title.split(" - ")[-1].strip() or "Unknown company"
            raw.append(
                {
                    "company_name": company[:250],
                    "domain": "",
                    "signal_type": "filing",
                    "source": "sec_edgar",
                    "title": title[:500],
                    "raw_data": {"filed_at": updated, "form": "8-K"},
                }
            )
        return raw[:10]
    except Exception as exc:  # noqa: BLE001 — collectors must never crash the run
        logger.warning("SEC EDGAR collector failed: %s", exc)
        return []


def _between(text: str, start: str, end: str) -> str:
    """Substring between two markers, or empty string."""
    try:
        return text.split(start, 1)[1].split(end, 1)[0].strip()
    except IndexError:
        return ""


async def collect_newsapi() -> list[dict]:
    """Company news via NewsAPI (requires NEWSAPI_KEY)."""
    if not settings.newsapi_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": '"appoints" OR "raises Series" OR "restructuring" OR "new CEO"',
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "apiKey": settings.newsapi_key,
                },
            )
            response.raise_for_status()
            articles = response.json().get("articles", [])
        results = []
        for article in articles:
            title = (article.get("title") or "").strip()
            if not title:
                continue
            source_name = (article.get("source") or {}).get("name", "")
            results.append(
                {
                    "company_name": title.split(" ")[0][:250] or "Unknown company",
                    "domain": "",
                    "signal_type": "news",
                    "source": "newsapi",
                    "title": title[:500],
                    "raw_data": {
                        "url": article.get("url"),
                        "published_at": article.get("publishedAt"),
                        "outlet": source_name,
                    },
                }
            )
        return results
    except Exception as exc:  # noqa: BLE001
        logger.warning("NewsAPI collector failed: %s", exc)
        return []


async def collect_crunchbase() -> list[dict]:
    """Funding rounds via Crunchbase (requires CRUNCHBASE_API_KEY)."""
    if not settings.crunchbase_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.crunchbase.com/api/v4/searches/funding_rounds",
                headers={"X-cb-user-key": settings.crunchbase_api_key},
                json={
                    "field_ids": ["identifier", "announced_on", "investment_type"],
                    "order": [{"field_id": "announced_on", "sort": "desc"}],
                    "limit": 10,
                },
            )
            response.raise_for_status()
            entities = response.json().get("entities", [])
        results = []
        for entity in entities:
            props = entity.get("properties", {})
            identifier = props.get("identifier", {}) or {}
            name = (identifier.get("value") or "").strip()
            if not name:
                continue
            results.append(
                {
                    "company_name": name[:250],
                    "domain": "",
                    "signal_type": "funding",
                    "source": "crunchbase",
                    "title": f"{name} announced a funding round"[:500],
                    "raw_data": {
                        "announced_on": props.get("announced_on"),
                        "investment_type": props.get("investment_type"),
                    },
                }
            )
        return results
    except Exception as exc:  # noqa: BLE001
        logger.warning("Crunchbase collector failed: %s", exc)
        return []


async def collect_job_boards() -> list[dict]:
    """Job-post signals. LinkedIn/Indeed have no free public API — demo data
    stands in until an Apollo/job-board integration key is configured."""
    return []


async def collect_sam_gov() -> list[dict]:
    """SAM.gov pre-solicitation notices (public API requires a key)."""
    return []


def demo_signals() -> list[dict]:
    """Realistic synthetic signals covering all 8 canonical types.

    Used when live collectors return nothing (no keys / offline) so the
    pipeline, scoring, and UI always have material to work with. Every
    record is flagged ``raw_data.demo = True``.
    """
    rows = [
        ("Meridian Health Systems", "meridianhealth.com", "job_post", "linkedin_jobs",
         "Hiring: VP of Digital Transformation, reports to CEO"),
        ("Atlas Logistics Group", "atlaslogistics.io", "leadership_change", "newsapi",
         "Atlas Logistics appoints former Flexport exec Dana Whitfield as COO"),
        ("Northwind SaaS", "northwind.app", "funding", "crunchbase",
         "Northwind raises $24M Series B led by Insight Partners"),
        ("Bayline County Schools", "baylinek12.org", "procurement_notice", "sam_gov",
         "RFI published: district-wide staff uniform and apparel program"),
        ("Corvus Fintech", "corvuspay.com", "earnings_language", "earnings_calls",
         "CFO on Q2 call: 'we are investing heavily in partner enablement this year'"),
        ("Helios Manufacturing", "heliosmfg.com", "tech_change", "builtwith",
         "Helios job posts now mention migrating from SAP to NetSuite"),
        ("Juniper Hospitality", "juniperhotels.com", "news", "newsapi",
         "Juniper Hospitality announces 12 new boutique properties across EU"),
        ("Vantage Robotics", "vantagerobotics.ai", "filing", "sec_edgar",
         "8-K filed: Vantage Robotics enters definitive merger agreement"),
    ]
    return [
        {
            "company_name": name,
            "domain": domain,
            "signal_type": stype,
            "source": source,
            "title": title,
            "raw_data": {"demo": True},
        }
        for name, domain, stype, source, title in rows
    ]


# --- Pipeline nodes ----------------------------------------------------------


async def _node_collect(state: dict) -> dict:
    """Run all collectors; fall back to demo signals when nothing was found."""
    collected: list[dict] = []
    for collector in (
        collect_sec_edgar,
        collect_newsapi,
        collect_crunchbase,
        collect_job_boards,
        collect_sam_gov,
    ):
        collected.extend(await collector())
    if not collected:
        logger.info("Signal Scout: no live signals collected, using demo batch")
        collected = demo_signals()
    return {"raw_signals": collected}


async def _node_normalize(state: dict) -> dict:
    """Drop malformed records and coerce required fields."""
    normalized = []
    for record in state.get("raw_signals", []):
        name = (record.get("company_name") or "").strip()
        stype = (record.get("signal_type") or "").strip()
        if not name or not stype:
            continue
        normalized.append(
            {
                "company_name": name,
                "domain": (record.get("domain") or "").strip(),
                "signal_type": stype,
                "source": (record.get("source") or "unknown").strip(),
                "title": (record.get("title") or "").strip(),
                "raw_data": record.get("raw_data") or {},
            }
        )
    return {"normalized_signals": normalized}


async def _node_dedupe(state: dict) -> dict:
    """Deduplicate within the batch by (company, type, title)."""
    seen: set = set()
    unique = []
    for record in state.get("normalized_signals", []):
        key = (record["company_name"].lower(), record["signal_type"], record["title"].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return {"deduped_signals": unique}


async def _node_persist(state: dict) -> dict:
    """Find-or-create accounts and insert new Signal rows (status ``new``).

    Skips signals whose (account, type, title) already exists in the DB so
    repeated scout runs stay idempotent.
    """
    db: AsyncSession = state["db"]
    org_id: uuid.UUID = state["org_id"]
    persisted = 0

    for record in state.get("deduped_signals", []):
        account = await _find_or_create_account(db, org_id, record)
        existing = await db.execute(
            select(Signal.id).where(
                Signal.account_id == account.id,
                Signal.signal_type == record["signal_type"],
                Signal.title == record["title"],
            )
        )
        if existing.scalars().first() is not None:
            continue
        db.add(
            Signal(
                account_id=account.id,
                signal_type=record["signal_type"],
                source=record["source"],
                title=record["title"],
                raw_data=record["raw_data"],
                status="new",
            )
        )
        persisted += 1

    await db.commit()
    logger.info("Signal Scout: persisted %d new signals for org %s", persisted, org_id)
    return {"persisted_count": persisted}


async def _find_or_create_account(
    db: AsyncSession, org_id: uuid.UUID, record: dict
) -> Account:
    """Match an account by company name within the org, creating if absent."""
    result = await db.execute(
        select(Account).where(
            Account.org_id == org_id,
            Account.company_name == record["company_name"],
        )
    )
    account: Optional[Account] = result.scalars().first()
    if account is None:
        account = Account(
            org_id=org_id,
            company_name=record["company_name"],
            domain=record["domain"],
        )
        db.add(account)
        await db.flush()
    return account


PIPELINE_NODES = [
    ("collect", _node_collect),
    ("normalize", _node_normalize),
    ("dedupe", _node_dedupe),
    ("persist", _node_persist),
]


async def run_signal_scout(org_id: uuid.UUID, db: AsyncSession) -> dict:
    """Execute the full scout pipeline for one organization."""
    pipeline = compile_pipeline("signal_scout", PIPELINE_NODES)
    return await pipeline.ainvoke({"org_id": org_id, "db": db})
