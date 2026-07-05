"""Demo seed: 1 org, 1 user, 1 ICP, 10 accounts, 20 signals, scored queue.

Run: ``python -m app.db.seed``. Idempotent — exits if the demo org exists.
Also creates the schema when tables are missing (dev convenience; production
uses Alembic).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from sqlalchemy import select

from app.db.models import (
    Account,
    Base,
    BusinessContextDoc,
    ICPProfile,
    Organization,
    Signal,
    User,
    utcnow,
)
from app.db.session import get_engine, get_session_factory

logger = logging.getLogger("nexus.seed")

DEMO_ORG_NAME = "NEXUS Demo Org"

# company, domain, industry, employees, revenue, geography, tech stack
ACCOUNTS = [
    ("Meridian Health Systems", "meridianhealth.com", "healthtech", 850, 120_000_000,
     "United States", {"crm": "Salesforce", "cloud": "AWS"}),
    ("Atlas Logistics Group", "atlaslogistics.io", "logistics", 420, 75_000_000,
     "United States", {"erp": "SAP", "cloud": "Azure"}),
    ("Northwind SaaS", "northwind.app", "saas", 95, 12_000_000,
     "United States", {"crm": "HubSpot", "cloud": "AWS", "analytics": "Segment"}),
    ("Bayline County Schools", "baylinek12.org", "education", 1200, 0,
     "United States", {}),
    ("Corvus Fintech", "corvuspay.com", "fintech", 210, 34_000_000,
     "United Kingdom", {"cloud": "GCP", "payments": "Stripe"}),
    ("Helios Manufacturing", "heliosmfg.com", "manufacturing", 640, 98_000_000,
     "Germany", {"erp": "SAP"}),
    ("Juniper Hospitality", "juniperhotels.com", "hospitality", 310, 45_000_000,
     "France", {"pms": "Opera"}),
    ("Vantage Robotics", "vantagerobotics.ai", "robotics", 150, 22_000_000,
     "United States", {"cloud": "AWS"}),
    ("Pemberton Legal", "pembertonlaw.com", "legal services", 75, 18_000_000,
     "United States", {"dms": "iManage"}),
    ("Solstice Energy", "solsticeenergy.co", "energy", 980, 210_000_000,
     "Canada", {"erp": "Oracle", "cloud": "Azure"}),
]

# company, signal_type, source, title, days_ago
SIGNALS = [
    ("Meridian Health Systems", "job_post", "linkedin_jobs",
     "Hiring: VP of Digital Transformation, reports directly to CEO", 3),
    ("Meridian Health Systems", "earnings_language", "earnings_calls",
     "CEO: 'modernizing our patient engagement stack is our top FY27 initiative'", 8),
    ("Meridian Health Systems", "leadership_change", "newsapi",
     "Meridian Health names ex-Epic executive Sarah Lindqvist as CIO", 12),
    ("Meridian Health Systems", "procurement_notice", "manual",
     "Meridian issues RFI for patient engagement transformation partner", 2),
    ("Atlas Logistics Group", "leadership_change", "newsapi",
     "Atlas Logistics appoints former Flexport exec Dana Whitfield as COO", 5),
    ("Atlas Logistics Group", "tech_change", "builtwith",
     "Atlas job posts now mention migrating from SAP to NetSuite", 15),
    ("Northwind SaaS", "funding", "crunchbase",
     "Northwind raises $24M Series B led by Insight Partners", 2),
    ("Northwind SaaS", "job_post", "linkedin_jobs",
     "Northwind hiring first VP Sales and 4 enterprise AEs", 6),
    ("Bayline County Schools", "procurement_notice", "sam_gov",
     "RFI published: district-wide staff uniform and apparel program", 4),
    ("Bayline County Schools", "news", "newsapi",
     "Bayline board approves $3.2M operations modernization budget", 20),
    ("Corvus Fintech", "earnings_language", "earnings_calls",
     "CFO on Q2 call: 'we are investing heavily in partner enablement this year'", 7),
    ("Corvus Fintech", "job_post", "linkedin_jobs",
     "Corvus hiring Head of Partnerships (new role)", 10),
    ("Helios Manufacturing", "tech_change", "builtwith",
     "Helios job posts reference NetSuite migration and new integration lead", 9),
    ("Helios Manufacturing", "filing", "sec_edgar",
     "Helios AG files notice of restructuring of North American operations", 18),
    ("Juniper Hospitality", "news", "newsapi",
     "Juniper Hospitality announces 12 new boutique properties across EU", 6),
    ("Juniper Hospitality", "job_post", "linkedin_jobs",
     "Juniper hiring Director of Procurement, hotel operations", 11),
    ("Vantage Robotics", "filing", "sec_edgar",
     "8-K filed: Vantage Robotics enters definitive merger agreement", 1),
    ("Vantage Robotics", "funding", "crunchbase",
     "Vantage Robotics closes $40M Series C", 30),
    ("Pemberton Legal", "leadership_change", "newsapi",
     "Pemberton Legal elects new managing partner effective immediately", 14),
    ("Solstice Energy", "earnings_language", "earnings_calls",
     "Solstice CEO: 'digital field operations is where the next dollar goes'", 13),
    ("Solstice Energy", "job_post", "linkedin_jobs",
     "Solstice hiring Program Director, Vendor Consolidation", 4),
    ("Solstice Energy", "procurement_notice", "sam_gov",
     "Solstice publishes pre-solicitation notice for digital field operations vendor", 3),
]

CONTEXT_DOCS = [
    ("case_study", "Won: Meridian-scale healthtech transformation",
     "We won a $180K engagement with a 900-person healthtech provider by engaging the "
     "incoming CIO within 3 weeks of her appointment, before any RFP existed. Key: we "
     "framed the cost of a stalled patient-engagement roadmap at $40K/month."),
    ("win_loss", "Lost: waited for the RFP at a logistics firm",
     "We lost a $220K logistics modernization deal because we responded to the RFP "
     "instead of originating it. The winner had been advising the new COO for two "
     "months before the RFP was drafted. Lesson: leadership change = 90 day window."),
    ("pricing", "Standard engagement pricing",
     "Discovery sprint: $15K fixed, 2 weeks. Transformation roadmap: $45K, 6 weeks. "
     "Full implementation advisory: $120K-$250K, 4-8 months. Retainer: $8K/month."),
]


async def seed() -> None:
    """Create schema if needed and populate demo data (idempotent)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = get_session_factory()
    async with factory() as db:
        existing = (
            await db.execute(
                select(Organization).where(Organization.name == DEMO_ORG_NAME)
            )
        ).scalars().first()
        if existing is not None:
            logger.info("Demo org already exists (%s), skipping seed", existing.id)
            print(f"Already seeded. Demo org id: {existing.id}")
            return

        org = Organization(name=DEMO_ORG_NAME, plan="agency", api_credits_remaining=500)
        db.add(org)
        await db.flush()

        db.add(User(email="demo@nexusintelligence.app", name="Demo Founder", org_id=org.id, plan_tier="agency"))
        db.add(
            ICPProfile(
                org_id=org.id,
                target_industries=[
                    "healthtech", "logistics", "saas", "fintech",
                    "hospitality", "education", "energy",
                ],
                company_size_min=50,
                company_size_max=1500,
                titles_targeted=["CEO", "COO", "CIO", "VP Operations", "Head of Procurement"],
                geographies=["United States", "United Kingdom", "Germany", "France", "Canada"],
                tech_stack_keywords=["Salesforce", "SAP", "NetSuite", "AWS", "Oracle", "Azure"],
                offer_description=(
                    "B2B operations transformation consulting: we help mid-market "
                    "companies modernize operations after leadership changes, funding "
                    "rounds, or restructuring, typically $45K-$250K engagements."
                ),
            )
        )
        for doc_type, title, content in CONTEXT_DOCS:
            db.add(BusinessContextDoc(org_id=org.id, doc_type=doc_type, title=title, content=content))

        accounts: dict = {}
        for name, domain, industry, employees, revenue, geo, tech in ACCOUNTS:
            account = Account(
                org_id=org.id, company_name=name, domain=domain, industry=industry,
                employee_count=employees, revenue_estimate=revenue, geography=geo,
                tech_stack=tech,
            )
            db.add(account)
            accounts[name] = account
        await db.flush()

        now = utcnow()
        for company, signal_type, source, title, days_ago in SIGNALS:
            db.add(
                Signal(
                    account_id=accounts[company].id,
                    signal_type=signal_type,
                    source=source,
                    title=title,
                    raw_data={"demo": True},
                    detected_at=now - timedelta(days=days_ago),
                    status="new",
                )
            )
        await db.commit()

        # Classify (heuristics in demo mode), then score + fill the queue.
        from app.agents.intent_classifier import run_intent_classifier
        from app.services.queue import refresh_action_queue

        await run_intent_classifier(org.id, db)
        entries = await refresh_action_queue(db, org.id)

        print(f"Seeded demo org: {org.id}")
        print(f"Accounts: {len(accounts)}, signals: {len(SIGNALS)}, queue entries: {len(entries)}")
        for entry in entries:
            print(f"  NEXUS {entry.nexus_score}: {entry.signal_summary[:80]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())
