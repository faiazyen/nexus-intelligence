# NEXUS Intelligence — Handoff

**Session end:** 2026-07-06 (deploy session)
**Repo:** `faiazyen/nexus-intelligence` (private) — single branch, `main`. No feature
branches exist; every commit this session went straight to `main` and is pushed.
Nothing pending to commit or merge.

## Deploy session (2026-07-06, second entry same day)

Frontend is live: **https://nexus-intelligence-murex.vercel.app** (Vercel project
`nexus-intelligence`, team `faiazyens-projects`). Manual `vercel deploy --prod`
from `frontend/` — no GitHub auto-deploy wired up yet, so future pushes to `main`
won't redeploy it automatically.

Backend is NOT deployed yet — `render.yaml` is committed (`9cc3ea0`) as a Render
Blueprint (web service + free Postgres, runs `alembic upgrade head` before
uvicorn) but nobody has connected the GitHub repo to a Render account and clicked
"Apply" yet. That's the very next step.

Also in `9cc3ea0`: `backend/app/core/config.py` now normalizes a bare
`postgresql://` URL to `postgresql+asyncpg://` — Render's (and most managed
Postgres providers') connection string doesn't include the driver, and the
async SQLAlchemy engine requires it. Verified with the local `.venv` and the
full test suite (71 passed, 3 skipped) — no regressions.

**QA on the live frontend (demo mode, no backend yet):**
- Marketing site and dashboard render clean, no console errors, "DEMO STREAM"
  badge correctly signals mock data on Command Center.
- Confirmed real interaction (asked Business Brain "who should I call today?")
  correctly attempts `http://localhost:8001/api/v1/brain/briefing` — this is
  expected: `NEXT_PUBLIC_API_URL` is currently set to the old localhost value
  as a placeholder (Next.js inlines `NEXT_PUBLIC_*` at build time, so this
  needs a rebuild once the backend URL exists, not just an env var change).
- One transient 503 on an account-detail RSC prefetch (`acc_hartwell_industrial`)
  during a burst of simultaneous nav-link prefetches — reproduced once, not on
  direct navigation to the same URL afterward. Likely a serverless cold-start
  blip, not a code bug. Worth a second look if it recurs under real traffic.
- **Did not verify Vercel Deployment Protection (password gate)** — the CLI has
  no flag for it and the linked account may be on the Hobby plan, where it's
  Pro-only. The app has zero server-side auth (per the existing audit), so
  until either Deployment Protection or real auth exists, anyone with the URL
  can hit it. Mitigations already in place: `$0.25/day` hard LLM spend cap,
  and no `OPENROUTER_API_KEY` has been added to Vercel by this session — only
  add it once you've checked Deployment Protection availability on the
  Vercel dashboard (Project Settings → Deployment Protection).

**To finish the deploy (next session or right now):**
1. Go to Render → New → Blueprint → connect `faiazyen/nexus-intelligence` →
   it'll read `render.yaml` and provision the DB + web service. Set
   `OPENROUTER_API_KEY` / `APOLLO_API_KEY` / `CORS_ORIGINS` (to the Vercel URL
   above) in the Render dashboard — they're marked `sync: false` in the
   blueprint so Render will prompt for them instead of committing secrets.
2. Copy the Render backend URL, then:
   `cd frontend && vercel env rm NEXT_PUBLIC_API_URL production` (confirm),
   then `vercel env add NEXT_PUBLIC_API_URL production --value <render-url> --yes`,
   then `vercel deploy --prod --yes` to rebuild with the real URL baked in.
3. Re-run the Business Brain click-through test to confirm the API call
   succeeds against the live backend instead of localhost.

## What's live on `main` right now

1. **Full build** — FastAPI backend, Next.js frontend, 6-agent LangGraph pipeline,
   Postgres schema, GTM kit. (`352f777`…`b880e73`)
2. **Live QA pass** — ran the whole stack for real (not mocks) and found + fixed 7
   integration bugs: LangGraph silently dropping state between nodes, `.env`
   resolution depending on cwd, a hardcoded org-id header masking every live
   response with demo data, two "eager fallback evaluation" bugs that broke
   outreach generation and account profiles for any real account, an SSE framing
   bug that rendered Brain chat as one unreadable run-on string, an em dash in
   the daily briefing violating the standing no-em-dash rule, and a
   snake_case/camelCase mismatch that silently discarded every ICP settings edit.
   (`fcc4c6b`)
3. **Brutal product audit** — [docs/PRODUCT_AUDIT_AND_MVP.md](PRODUCT_AUDIT_AND_MVP.md).
   Headline finding: only 1 of 8 claimed signal types (SEC 8-K filings) has a real
   collector; job postings and procurement notices — the two signals the whole
   "pre-RFP" thesis leans on — are `return []` today, 100% synthetic seed data so
   far. Contact enrichment doesn't exist server-side despite being shown in the
   UI. Redefines the MVP as a single-ICP dogfood loop inside Merch Maverick
   (hospitality vertical), one buyer (Faiaz), one metric (reply rate / meetings
   booked). Full prioritized fix list in section J. (`f6633d2`)
4. **Fix 10 — OpenRouter multi-model routing** — all LLM calls now route through
   OpenRouter (`backend/app/core/llm_router.py`): free tier → ultra-cheap tier →
   mid-tier reasoning (Kimi K2 Thinking) → Claude Opus 4.8 premium fallback, with
   every tier still backing onto the existing zero-cost heuristic/template
   fallbacks. Every model slug in the engineering ticket was checked against
   OpenRouter's live catalog and corrected where wrong (most of them were — see
   commit body for specifics). Cost tracking reads OpenRouter's real
   `usage.cost` per request rather than a hardcoded price table. Dropped Redis
   entirely (unused now); added `pipeline_events` audit table and
   `GET /api/v1/analytics/costs` + `/pipeline-events`. (`38c47ff`)

All 71 backend tests pass, frontend production build is clean, smoke-tested
classify/outreach end to end in demo mode, confirmed live in browser.

## Currently running locally (started this session, still up)

- Backend: `uvicorn` on **:8001** (not :8000 — a stray unrelated process from a
  different project already held :8000; see `.claude/launch.json` in the Merch
  Maverick worktree if you need the exact command)
- Frontend: `next dev` on **:3000**, `.env.local` points `NEXT_PUBLIC_API_URL` at
  :8001
- Database: an isolated `nexus` database/role inside your **existing** local
  Supabase Postgres container (port 54322) — not the nexus-intelligence
  `docker-compose.yml` stack (that image pull stalled mid-session; never
  retried). `DATABASE_URL` in `nexus-intelligence/.env` points there.
- `ANTHROPIC_API_KEY`/`OPENROUTER_API_KEY` are both empty — everything tested so
  far ran in demo mode. **No real LLM cost has ever been measured.**

To restart cleanly next session:
```bash
cd nexus-intelligence
# backend
cd backend && ./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
# frontend (separate terminal)
cd frontend && npm run dev
```
If the frontend dev server ever 500s with `MODULE_NOT_FOUND` on `_document.js`,
that's `.next` cache corruption from running `next build` in the same directory
while `next dev` is live (happened twice this session) — `rm -rf .next` and
restart, don't debug it.

## What's NOT done yet (the actual next steps)

The audit (section J) and Fix 10 are two different things — Fix 10 only replaced
the LLM call layer. The audit's broader MVP redesign is still entirely undone:

**Critical blockers before any real dogfood run (audit section J):**
1. A real signal source for the hospitality vertical — `collect_job_boards()` and
   `collect_sam_gov()` still just `return []`. Even a manual-entry form counts.
2. Cut/hide the 3-persona marketing site (`/solo` `/agency` `/gtm`), pricing page,
   onboarding wizard — none of this has been touched.
3. Basic auth gate — still zero auth beyond an `X-Org-Id` header defaulting to
   the seeded demo org. Fine on localhost, not fine anywhere else.
4. ~~Audit/event log~~ — done via `pipeline_events` in Fix 10, but only wired for
   scout/classifier/scorer stage failures, not a "mark outreach as sent" action
   (the `sent_at`/`outcome` columns still have no UI path that sets them).

**High-priority, not started:**
- Real contact enrichment (Apollo key is configured, never called)
- Real cost-per-account measurement — needs a live `OPENROUTER_API_KEY` in `.env`
- The 50-signal manual precision-labeling loop
- Adversarial prompt-injection test signals through the classifier/writer

**Explicitly parked (per the audit, do not start without discussing first):**
- Collapsing the 6-agent LangGraph pipeline to a single script (audit section F)
  — LangGraph is still in place; Fix 10 didn't touch the orchestration layer
- Dropping Qdrant (still an unused dependency, pre-existing, out of scope twice now)
- The Obsidian-inspired knowledge-graph rework for Business Brain — discussed,
  never scoped into a plan, not started
- Billing/Stripe, multi-tenant org management, expansion personas, Enterprise tier

**Known pre-existing gap, not introduced this session:** the Terraform ECS config
references an `aws_secretsmanager_secret.openrouter_api_key` resource that is
never actually declared anywhere in the `.tf` files — same gap existed under the
old `anthropic_api_key` name before Fix 10 renamed it. This Terraform has never
been applied to real AWS infra.

## Suggested next session

Pick up at audit section J, critical blocker #1: get one real signal flowing
(manual entry is fine) for the hospitality vertical, then work down the list in
order. Don't start on the parked items without checking in first — that list
exists specifically to stop scope creep after a session that already found the
product's vision running well ahead of its plumbing.
