# NEXUS INTELLIGENCE

**Know who's about to buy. Before anyone else does.**

NEXUS is a B2B pre-RFP signal intelligence platform. It monitors 10,000+ daily signals
(job posts, SEC filings, leadership changes, procurement notices, funding, earnings
language), reasons about them through the lens of *your* business, scores every account
by urgency, ICP fit, and budget probability, and routes hot accounts to an Action Queue
with signal-specific outreach ready to send.

Two products, one loop:

- **NEXUS BRAIN** — an AI business intelligence layer that learns your ICP, offer, past
  wins, and competitors via RAG, and acts as your strategic advisor (daily briefings,
  deal coaching, proposal drafts).
- **NEXUS INTENT** — a 6-agent LangGraph system that monitors, classifies, scores, and
  activates buying signals months before the RFP exists.

> **Before building on this:** read
> [docs/PRODUCT_AUDIT_AND_MVP.md](docs/PRODUCT_AUDIT_AND_MVP.md) — a brutally honest
> audit of what's real vs. speculative in this repo (only 1 of 8 claimed signal types
> has a working collector) and the scoped 30-day MVP this product is actually being
> validated against.

## Quick start

```bash
cp .env.example .env        # add your OPENROUTER_API_KEY
docker-compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (docs at /docs)
- Seed demo data: `docker-compose exec backend python -m app.db.seed`

## Repo layout

```
backend/          FastAPI (async) + SQLAlchemy 2.0 + LangGraph agents
frontend/         Next.js 14 App Router, TypeScript strict, Tailwind
infrastructure/   Dockerfiles, Terraform (AWS ECS/RDS/ElastiCache/S3)
docs/             Architecture, API reference, build contract, GTM package
```

## LLM routing (beta configuration)

All LLM calls route through OpenRouter (`backend/app/core/llm_router.py`) — one API
key, one SDK, no separate Anthropic key. Every slug below was checked against
OpenRouter's live `/api/v1/models` catalog at the time this was written; that catalog
(pricing especially) moves fast, so treat this table as a snapshot, not a permanent
fact — verify again before trusting it for a real budget decision.

```
┌────────────────────────────────────────────────────────────────────────┐
│              NEXUS LLM ROUTING — BETA CONFIGURATION                    │
├────────────────┬──────────────────────────────────────────┬────────────┤
│ Task           │ Model (OpenRouter slug)                   │ Price/1M   │
├────────────────┼──────────────────────────────────────────┼────────────┤
│ Classification │ nvidia/nemotron-3-nano-omni-30b-a3b-      │ free       │
│ (tier 0)       │   reasoning:free                          │            │
│ Classification │ deepseek/deepseek-v4-flash                │ $0.09/$0.18│
│ (tier 1 fallbk)│                                            │            │
│ Outreach Gen   │ moonshotai/kimi-k2-thinking                │ $0.60/$2.50│
│ Brain Q&A      │ moonshotai/kimi-k2-thinking                │ $0.60/$2.50│
│ Fallback (tier 3, quality-gate or error escalation only)    │            │
│                │ anthropic/claude-opus-4.8                  │ $5.00/$25  │
├────────────────┴──────────────────────────────────────────┴────────────┤
│ Cost accounting: OpenRouter returns the real per-request cost in every │
│ response (`usage.cost`) — this is read directly rather than estimated │
│ from the table above wherever possible. See GET /api/v1/analytics/costs│
│ for actual measured spend once a real key is in place.                │
│                                                                          │
│ Hard daily limit: $0.25 (NEXUS_DAILY_LLM_LIMIT) — over budget routes   │
│ everything to the free tier / rule-based fallback and logs an alert.   │
└──────────────────────────────────────────────────────────────────────────┘
```

Every task has a zero-cost, zero-network final fallback that can never fail outright:
the rule-based heuristic classifier or the deterministic outreach template. Real cost
per account monitored has not yet been measured against production signal volume —
per `docs/PRODUCT_AUDIT_AND_MVP.md` section G, that's a testing-plan item, not an
assumption to build a pricing page on.

## Docs

- [Build contract](docs/CONTRACT.md) — canonical schema, API surface, conventions
- [Master product document](docs/MASTER_PRODUCT_DOCUMENT.md) — full product bible
- [Architecture](docs/architecture.md) · [API reference](docs/api-reference.md)
- [GTM launch package](docs/gtm/)

## Development

```bash
# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend
cd frontend && npm install && npm run dev

# tests
cd backend && pytest
cd frontend && npm test
```
