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

## Quick start

```bash
cp .env.example .env        # add your ANTHROPIC_API_KEY
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
