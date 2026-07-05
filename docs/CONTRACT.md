# NEXUS INTELLIGENCE — Build Contract

Single source of truth for every workstream. **Do not deviate from names, paths, or tokens
defined here.** If something is ambiguous, follow the Master Product Document
(`docs/MASTER_PRODUCT_DOCUMENT.md`) — this contract wins on conflicts.

## Repo layout

```
nexus-intelligence/
├── backend/                  # Python 3.12, FastAPI async
│   ├── app/
│   │   ├── main.py           # FastAPI app factory, router mounting, CORS
│   │   ├── core/config.py    # pydantic-settings Settings (PROVIDED — do not rewrite)
│   │   ├── core/llm.py       # Anthropic client wrapper (agents workstream owns)
│   │   ├── db/models.py      # SQLAlchemy 2.0 models (PROVIDED — do not rewrite)
│   │   ├── db/session.py     # async engine + session factory (backend workstream)
│   │   ├── db/seed.py        # seed script: 10 accounts, 20 signals (backend)
│   │   ├── routers/          # brain.py, intent.py, signals.py, analytics.py
│   │   ├── services/         # scoring.py + business logic (backend)
│   │   └── agents/           # 6 agents + supervisor (agents workstream owns)
│   ├── alembic/              # migrations, revision 001_initial
│   ├── tests/                # pytest
│   └── requirements.txt      # PROVIDED
├── frontend/                 # Next.js 14 App Router, TypeScript strict, Tailwind
├── infrastructure/           # Dockerfiles, terraform/
├── docker-compose.yml        # repo root (infra workstream)
├── .github/workflows/ci.yml  # (infra workstream)
└── docs/
```

## Ownership boundaries (parallel-safe)

| Workstream | Owns (writes ONLY here) |
|---|---|
| backend-api | `backend/app/main.py`, `db/session.py`, `db/seed.py`, `routers/`, `services/`, `alembic/`, `backend/tests/` (except `tests/agents/`) |
| agent-system | `backend/app/agents/`, `backend/app/core/llm.py`, `backend/app/core/prompts.py`, `backend/tests/agents/` |
| frontend | everything under `frontend/` |
| infra-gtm | `docker-compose*.yml`, `infrastructure/`, `.github/`, `docs/architecture.md`, `docs/api-reference.md`, `docs/gtm/` |

## Python conventions

- Target Python 3.12 in Docker, but **do not use `match` statements** (local dev machine
  runs 3.9 for syntax checks). `list[str]`/`X | None` annotations are fine.
- Async everywhere: `asyncpg` + `AsyncSession`, `httpx.AsyncClient`.
- Import models as `from app.db.models import Account, Signal, ...` — exact class names below.
- All Claude calls go through `app.core.llm.claude_call()` (agents workstream implements):
  `async def claude_call(*, model: str, system: str, messages: list[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str`
  with 3-attempt exponential backoff (1s/2s/4s), token usage logging, and a
  `LLMUnavailableError` fallback. Model tiers from `Settings`: `settings.model_opus`,
  `settings.model_sonnet`, `settings.model_haiku`.

## DB model class names (defined in db/models.py — import, never redefine)

`User`, `Organization`, `ICPProfile`, `BusinessContextDoc`, `Signal`, `Account`,
`AccountScore`, `ActionQueueEntry`, `OutreachDraft`, `BrainConversation`, `BrainBriefing`

## Scoring engine (backend/app/services/scoring.py)

```python
def compute_urgency(signals: list[Signal], now: datetime) -> int          # 0-100
def compute_fit(account: Account, icp: ICPProfile) -> int                 # 0-100
def compute_budget_probability(signals: list[Signal]) -> int             # 0-100, additive caps at 100
def compute_nexus_score(urgency: int, fit: int, budget: int) -> int      # (u*f*b)/10000, 0-100
QUEUE_THRESHOLD = 70
SIGNAL_BUDGET_WEIGHTS = {"job_post": 15, "funding": 25, "leadership_change": 20,
                         "earnings_language": 30, "procurement_notice": 40,
                         "tech_change": 10, "news": 5, "filing": 10}
TIMING_WINDOWS_DAYS = {"leadership_change": 90, "funding": 60, "job_post": 45,
                       "procurement_notice": 120, "earnings_language": 60,
                       "tech_change": 45, "news": 30, "filing": 90}
```

Signal types (canonical strings): `job_post`, `leadership_change`, `funding`,
`procurement_notice`, `earnings_language`, `tech_change`, `news`, `filing`.
Urgency tiers: `HOT`, `WARM`, `COOL`. Statuses: signal `new|classified|scored|archived`,
queue `pending|outreach_generated|contacted|dismissed|converted`.

## API surface (mounted under /api/v1)

```
POST /api/v1/brain/onboard            multipart/JSON docs → business_context ingestion
GET  /api/v1/brain/briefing           latest BrainBriefing (generate on miss)
POST /api/v1/brain/ask                {"question": str} → StreamingResponse (SSE tokens)
GET  /api/v1/brain/deal/{id}/coach    deal coaching for an action-queue entry
GET  /api/v1/intent/queue             Action Queue entries, score desc, joined account+signals
GET  /api/v1/intent/account/{id}      full account profile + signal timeline + scores
POST /api/v1/intent/outreach/{id}     generate 3-variant outreach for account id
PUT  /api/v1/intent/icp               upsert ICP profile
GET  /api/v1/signals/stream           SSE stream of new signals
POST /api/v1/signals/custom           manually add a signal
GET  /api/v1/signals/history/{days}   signals for last N days
GET  /api/v1/analytics/pipeline       funnel: signals → scored → queued → contacted → replied
GET  /api/v1/analytics/signals        counts by type/tier for charting
GET  /health                          {"status":"ok"}
```

Auth: MVP uses header `X-Org-Id` (UUID) resolved to Organization; a `get_current_org`
dependency in `app/routers/deps.py`. Clerk integration stubbed behind it.

## Frontend contract

- Next.js 14 App Router, TypeScript strict, Tailwind. Package manager: npm.
- API base: `process.env.NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).
- Every fetch falls back to bundled demo fixtures (`frontend/src/lib/demo-data.ts`)
  when the API is unreachable — the app must demo standalone.
- Routes: `/` `/solo` `/agency` `/gtm` (marketing) and `/app` (command center),
  `/app/queue`, `/app/brain`, `/app/accounts/[id]`, `/app/signals`, `/app/settings`,
  `/app/onboarding` (6-step).
- Design tokens (CSS variables in globals.css, mirrored in Tailwind config):
  `--nexus-bg:#0A0E1A --nexus-surface:#111827 --nexus-border:#1F2937 --nexus-cyan:#22D3EE
   --nexus-emerald:#10B981 --nexus-amber:#F59E0B --nexus-red:#EF4444 --nexus-text:#F9FAFB
   --nexus-muted:#9CA3AF`
- Feel: Bloomberg Terminal meets Notion. Dark only. Data-dense, zero decorative fluff.

## Services (docker-compose, root)

| service | image/build | port |
|---|---|---|
| postgres | postgres:16-alpine | 5432 |
| qdrant | qdrant/qdrant | 6333 |
| backend | backend/Dockerfile | 8000 |
| frontend | frontend/Dockerfile | 3000 |

All LLM calls route through OpenRouter (`app/core/llm_router.py`) — one key,
one SDK, no Redis (the daily cost tracker is a plain JSONL file under
`backend/logs/`). See `app/core/llm_router.py`'s module docstring for the
verified model tiers.

Env var names (see `.env.example`): `DATABASE_URL`, `QDRANT_URL`,
`OPENROUTER_API_KEY`, `NEXUS_LLM_CLASSIFIER`, `NEXUS_LLM_CLASSIFIER_FALLBACK`,
`NEXUS_LLM_OUTREACH`, `NEXUS_LLM_BRAIN`, `NEXUS_LLM_FALLBACK`,
`NEXUS_DAILY_LLM_LIMIT`, `NEXUS_DISABLE_CLAUDE`, `APOLLO_API_KEY`,
`NEWSAPI_KEY`, `CRUNCHBASE_API_KEY`, `NEXT_PUBLIC_API_URL`.

## Copy rules (GTM + all outreach templates)

- Never use em dashes or double hyphens in any outreach copy, email sequence, or
  marketing copy. Use periods or commas instead.
- Banned phrases: "hope this finds you well", "circling back", "touching base",
  "synergy", "leverage", "value-add".
