# NEXUS Intelligence — Product Audit & 30-Day MVP Plan

**Prepared by:** Product / Engineering / GTM audit pass
**Date:** 2026-07-05
**Mandate:** Reduce risk, increase clarity, turn the current concept into a testable MVP usable inside Merch Maverick first. Not a vision expansion exercise.

**Method note:** every claim below about the codebase was verified directly against the repository (`faiazyen/nexus-intelligence`, branch `main`) as of this audit, not inferred from the original product document. Where a claim is unverifiable or speculative, it is labeled `[SPECULATIVE]`.

---

## A. Executive Audit Summary

NEXUS Intelligence today is a fully-built speculative SaaS product: a FastAPI backend, a Next.js frontend, a 6-agent LangGraph pipeline, a Postgres schema, and a complete GTM kit (Product Hunt copy, cold email sequence, LinkedIn calendar, investor one-pager). It has **zero real users, zero live paid data sources connected, and zero dogfood usage**. Everything that has ever run has run in demo mode against seeded, synthetic data.

The core idea — turn public buying signals into contextual, ready-to-send outreach ("signal-to-action reasoning") — is sound and genuinely differentiated versus Bombora/6sense/ZoomInfo, which stop at the data layer. Nothing about it has been validated with a real business, and several of its most-repeated claims don't survive contact with the actual code:

- Of the 8 signal types described in the product document, **only one (SEC 8-K filings) has a real, working, free data collector.** `collect_job_boards()` and `collect_sam_gov()` — the two collectors backing "job posting" and "procurement notice," the signals the entire "4–8 months before the RFP" thesis leans on hardest — are literally `return []`. Every job-post and procurement-notice signal that has ever appeared in this product is synthetic seed data.
- The product currently targets **three buyer personas** (solo consultant / agency / GTM team) with three marketing pages. That is scope-spread at a stage where scope-spread is the single most expensive mistake to make.
- Contact/decision-maker enrichment — shown in the UI as a "Contacts" tab — **does not exist server-side.** `apollo_api_key` is a config field referenced in one code comment and called nowhere. The tab is a frontend fixture.
- There is no authentication, no admin/audit layer, and no mechanism to mark a drafted message as actually sent — the `sent_at` / `outcome` columns exist in the schema, but no UI path ever sets them.
- The market-size and adoption statistics in the source product document trace almost entirely to SEO/content-marketing sites (growthspreeofficial.com, bizaigpt.com, marketbetter.ai, syncgtm.com, guideflow.com, miniloop.ai, dailyaiworld.com), not primary analyst research. Treat every number from that document as directionally suggestive at best — `[SPECULATIVE]` — never load-bearing for a real decision.

**Recommendation:** stop building outward-facing SaaS surface area. Redirect all effort into one internal dogfood loop inside Merch Maverick for 30 days. Replace the two fake data collectors with something real (even a manual-entry fallback beats a collector that silently returns nothing). Measure exactly one number: outreach reply rate / meetings booked from NEXUS-sourced signals, benchmarked against whatever Faiaz's outbound baseline is today.

---

## B. Misalignment Analysis

| # | Misalignment | Evidence |
|---|---|---|
| 1 | Claims of monitoring "10,000+ daily signals" vs. reality | Zero real signals have ever been monitored in production; only seed/demo data has flowed through the system. |
| 2 | Market-size claims presented as fact | Citations trace to SEO/content-marketing sites, not primary research (Gartner/Forrester-grade sourcing is absent). `[SPECULATIVE]` |
| 3 | Three ICPs targeted at once | `/solo`, `/agency`, `/gtm` marketing pages, three distinct headlines, three distinct pain narratives — this is the opposite of "narrow ICP." |
| 4 | Pricing set before cost is known | $299/$799/$2,499 tiers were written in the source doc before a single dollar of real Anthropic spend was measured. The "$0.50/day/100 accounts" guardrail is a code comment, never validated against real billing. |
| 5 | GTM assumes strangers are the first customer | The cold-email sequence and Product Hunt kit target external, cold consultants for a product with zero track record — the highest-risk, lowest-leverage way to get a first data point. |
| 6 | Architecture complexity exceeds workflow complexity | The actual MVP workflow is 4 sequential steps (collect → classify → score → draft). It is currently implemented as 6 coordinated LangGraph agents plus a supervisor plus a memory manager. The LangGraph state-loss bug found during QA (nodes silently dropping `db`/`org_id` between steps) was a direct, avoidable consequence of this complexity. |
| 7 | "Business Brain" framed as AI reasoning, implemented as keyword search | `rank_documents()` in `business_brain.py` is a term-overlap scoring function over pasted text blobs. It will feel underwhelming to any real user expecting the framing in the product document. |
| 8 | "Contacts" feature shown as working, not implemented | Contact enrichment is entirely a frontend fixture (`demoAccountProfile`'s `recommendedContacts`); nothing in the backend calls Apollo or any enrichment source. |

---

## C. Missing Capabilities

Ranked by how much they block a real dogfood test:

1. **Real signal collectors for the two flagship signal types.** Job postings and procurement notices — the ones the whole "pre-RFP" thesis depends on — have no implementation.
2. **Contact/decision-maker enrichment.** No backend enrichment call exists anywhere, despite `APOLLO_API_KEY` being a configured setting.
3. **Authentication / identity.** `X-Org-Id` header only, with a fallback to a single seeded demo org. No login, no session, no per-user permissions. This is fine for a single-user internal tool run on localhost; it is not fine the moment it's exposed anywhere else.
4. **Admin/audit trail.** No table, no endpoint, no UI shows why a signal was classified a certain way, what the pipeline did on a given day, or a way to override/undo a decision.
5. **Outcome tracking loop.** `sent_at` and `outcome` exist in the schema. Nothing in the product ever sets them — there's no "I sent this" action anywhere in the UI.
6. **Signal precision/recall measurement.** No ground-truth labels, no evaluation harness, no number for how often a "HOT" signal is actually a real buying trigger versus noise.
7. **Prompt-injection defenses on ingested signal content.** Signal titles/summaries originate from external, less-trusted sources (job boards, news, filings) and flow directly into LLM prompts and the UI. There is no sanitization layer today.
8. **Legal/ToS review of data collection methods.** LinkedIn-based collection is a well-documented litigation target (hiQ v. LinkedIn, Meta v. Bright Data). The product document assumes this is a viable free data source; it is a legal liability if implemented via scraping.
9. **Rate limiting / abuse controls** on the public API surface.
10. **Load/latency validation beyond a single user.** The signal SSE endpoint polls the database every 3 seconds per open connection with no connection cap — untested past one browser tab.

---

## D. Product-Market-Fit Assessment

**Current PMF evidence: none.** No paying customer, no design partner, no letter of intent, no waitlist beyond the AI-authored GTM package that has never been sent to a real human.

The only PMF hypothesis currently testable with existing resources is **dogfood-PMF, not market-PMF**: does this tool get Faiaz more/faster meetings for Merch Maverick than his status quo? That is fully knowable in 30 days without building anything new for an external market.

Recommendation: explicitly re-label the 3-persona marketing site, the pricing tiers, and the investor one-pager as **post-validation assets**. Pause all further work on them until the dogfood loop produces a real number.

---

## E. MVP Redesign — 30 Days, One ICP, One Buyer, One Use Case, One Metric

| Dimension | Decision |
|---|---|
| **ICP** | Hospitality operators (hotels, resorts, hospitality groups) in Merch Maverick's target geography — one vertical, not three. (Chosen because Merch Maverick's own marketing content already has hospitality-vertical work in progress, per its own repo's recent commit history — this is the path of least new effort.) |
| **Buyer** | Faiaz, acting as Merch Maverick's own growth/outbound function. Internal user, not an external SaaS customer. |
| **Use case** | Every morning, NEXUS surfaces up to 5 hospitality accounts with one *verifiable* trigger (new property opening, renovation, rebrand, expansion, new GM/ops-lead hire) and one drafted outreach message per account offering merch/uniform sourcing, referencing that exact trigger. |
| **Metric** | Reply rate and meetings booked over 30 days from NEXUS-sourced outreach, benchmarked against Faiaz's existing outbound baseline (if the baseline is "none," the bar is simply: meetings booked > 0 proves the loop works at all). |

**Explicit cuts for the 30-day window:**
- No multi-tenant org management, no billing/Stripe
- No `/solo`, `/agency`, `/gtm` marketing pages or persona split
- No Enterprise tier, no pricing page
- No LangGraph supervisor/6-agent orchestration — replace with a single daily script
- No Qdrant/vector RAG — one org's business context fits directly in a prompt
- No Redis-backed cost tracker — log spend to a file, it's one user
- No onboarding wizard — Faiaz's ICP and offer are already known; hardcode them

---

## F. Architecture Changes

**Collapse the pipeline.** Replace the 6-agent + supervisor LangGraph system with a single daily script that runs 4 steps in order: collect → classify → score → draft. At one org, one vertical, running once a day, there is no coordination problem for a graph orchestrator to solve — there is only a bug surface for one to create. (This is not speculative: the LangGraph state-loss bug found during the live QA pass on this exact system was a direct product of that complexity.)

**Drop Qdrant.** A handful of pasted business-context documents for one org fits entirely inside a single prompt's context window. A vector database solves a retrieval-at-scale problem that does not exist at this stage.

**Drop the Redis cost tracker.** Log every Claude API call's token usage and estimated cost to a plain file. One user does not need a distributed rate limiter.

**Keep, unchanged — these are real strengths:**
- The deterministic scoring formula (`urgency × fit × budget / 10000`) — genuinely rules-based, testable, explainable. Do not touch it.
- The outreach quality gate (banned phrases, sentence-count limit, em-dash/double-hyphen ban, signal-reference requirement) — also rules-based, also a real strength. Extend it (see H) rather than replace it.
- The "demo mode everywhere" fallback pattern — a good practice that let this whole system be tested without live credentials. Keep it as the default state for any new component.

**Replace the two dead collectors.** `collect_job_boards()` and `collect_sam_gov()` currently return `[]`. Replace both with either: (a) a manual signal-entry form where Faiaz pastes in a trigger he already noticed (perfectly valid at 5 accounts/day), or (b) one paid, ToS-compliant hospitality-industry news/press-release feed. Do not ship another collector that silently does nothing.

**Add a minimal audit log.** One `pipeline_events` table: every signal → classification → score → draft decision gets one row Faiaz can scroll through. This is the single highest-leverage trust-building feature for an internal tool, and it currently does not exist at all.

---

## G. Testing and Evaluation Plan

| Test | Method | Target |
|---|---|---|
| **Signal precision** | Faiaz manually labels the first 50 real detected signals (true trigger vs. noise) over weeks 1–2 | ≥70% precision before trusting the queue unattended. Recall is secondary — a missed signal costs a missed lead; a false-positive signal costs brand damage from a bad cold email, which is worse at this stage. |
| **Outreach quality** | Every draft is reviewed by Faiaz before send for the full 30 days — no auto-send under any condition | <30% "needs a full rewrite" rate by day 30, tracked as a simple tally |
| **Hallucination check** | 20 held-out "Ask the Brain" questions run weekly; every factual claim manually traced to an ingested document or real signal | Zero tolerance for fabricated account facts |
| **Prompt injection** | Adversarial test signals ("ignore previous instructions...", embedded fake system messages) run through the classifier and outreach writer | Confirm output isn't hijacked; extend the existing rule-based quality gate to flag/strip instruction-like text in raw signal titles before they reach any agent |
| **Latency** | Outreach generation (interactive, one user waiting) | <10s p95. The overnight signal pipeline has no hard SLA at 1-org scale — minutes is fine. |
| **Uptime** | No formal SLA needed for a single-user internal tool | Track manually: "did the pipeline run this morning?" for 30 straight days |
| **Cost per account monitored** | Instrument real Anthropic token usage per pipeline run once a live API key is in place | Get a real number before this is ever discussed again in a pricing conversation |

---

## H. Security and Compliance Review

- **Auth:** none exists today. Acceptable only while this stays on localhost for a single internal user. The moment it's deployed anywhere reachable beyond that, add a login gate before anything else.
- **Data collection legality:** drop any plan to scrape LinkedIn directly — it is an active litigation target (hiQ v. LinkedIn, Meta v. Bright Data). Use only sources with an explicit allowance for programmatic access: SEC EDGAR is genuinely free/public; prefer a licensed press-release/industry-news vendor over scraping for the rest.
- **PII handling:** the moment real contact enrichment is added (a decision-maker's name/email), that is regulated personal data. Write down a lawful basis (legitimate interest is the common basis for B2B outreach under GDPR, but it should be a deliberate documented decision, not a default) and have a way to honor an opt-out/erasure request.
- **Prompt injection surface:** signal content from external, adversarial-capable sources (job posts, news) flows straight into LLM prompts. Add a sanitization pass before ingestion; keep the existing outreach quality gate as a second line of defense — it is already doing real, valuable work here even though it wasn't originally designed for this threat.
- **Secrets hygiene:** spot-checked — the cost tracker logs `cost_usd` figures, not key material. Confirm the same discipline for any new enrichment provider before it's wired in.
- **XSS:** the Brain chat's markdown renderer escapes `&`/`<` before injecting formatting — a reasonable baseline, but re-review it any time it's extended, since the content it renders ultimately originates from external, less-trusted signal data.

---

## I. GTM Recommendations

**Phase 0 (this 30-day MVP): zero external GTM.** The only customer is Merch Maverick's own pipeline. Success is a number, not a launch.

**Phase 1 (only after Phase 0 produces a real number):** recruit 3–5 design partners by hand, through warm network — other small B2B sellers who want the same signal-to-action loop for their own outbound. Not a cold-email campaign off the AI-authored sequence.

**Phase 2 (only after Phase 1 validates with real, committed design partners):** revive the 3-persona marketing site, pricing tiers, and investor materials — narrowed to whichever single persona the design partners actually were, not all three at once.

**Kill or pause immediately:** the Product Hunt launch kit, the 30-day LinkedIn content calendar, and the investor one-pager. These are premature by at least two validation stages. Relaunch once there's a real number to put in them.

---

## J. Final Prioritized Fix List

**Critical blockers — must fix before any dogfood run:**
1. Get at least one real (or honestly manual) signal source flowing for the hospitality vertical — no more silently-empty collectors
2. Cut/hide the 3-persona marketing site, pricing page, and onboarding wizard
3. Add a basic auth gate if this is ever exposed off localhost
4. Add the minimal audit/event log so the pipeline stops being a black box
5. Enforce a manual-approval gate on every outreach send for the full 30-day test — no auto-send

**High-priority — fix during the 30 days, not before starting:**
6. Real contact enrichment, or explicitly remove the Contacts tab until it's real
7. Real cost-per-account measurement with a live Anthropic key
8. The 50-signal manual precision-labeling loop
9. A prompt-injection test pass on signal ingestion, and extend the quality gate to cover it

**Nice-to-have — explicitly post-validation, do not start now:**
10. Reintroducing LangGraph/multi-agent orchestration, if and when real multi-org concurrency exists
11. Qdrant/vector RAG, if and when business-context volume actually exceeds a single prompt's context window
12. The Obsidian-inspired knowledge-graph rework for Business Brain discussed separately — `[SPECULATIVE]`, explicitly parked, not part of this MVP
13. Billing/Stripe, multi-tenant org management
14. Expansion personas (agency, GTM team) and the Enterprise tier

---

## K. Revised Build Prompt for Engineering

```
NEXUS INTELLIGENCE — 30-DAY MVP BUILD PROMPT
Scope: single-org internal tool, hospitality vertical, one user (Faiaz).

Do NOT build: multi-tenant auth, billing, marketing site, persona pages,
LangGraph orchestration, Qdrant, Redis cost tracking, onboarding wizard.

DO build, in this order:

1. A single daily pipeline script (plain async function, no agent graph):
   collect -> classify -> score -> draft. Steps:
   a. Collect: keep the working SEC EDGAR collector. Replace the two
      dead collectors (job_boards, sam_gov) with a manual-entry form
      Faiaz can use to log a trigger he noticed himself. Do not ship
      another collector that returns [] silently.
   b. Classify: keep the existing rule-based heuristic as the DEFAULT
      path (it's real, tested, and free). Only call Claude Haiku when
      the heuristic can't confidently place a signal.
   c. Score: keep compute_urgency/compute_fit/compute_budget_probability
      exactly as-is. Do not touch this — it is the most solid part of
      the current system.
   d. Draft: keep the existing Outreach Writer + quality gate exactly
      as-is. Extend the quality gate to also reject/flag any signal
      title containing instruction-like language ("ignore previous
      instructions", "system:", etc.) before it reaches the writer.

2. A minimal audit log: one `pipeline_events` table, one row per
   pipeline decision, one page in the UI to scroll through it.

3. A "mark as sent" action on every outreach draft, wired to the
   existing sent_at column, and a simple "log the reply/outcome"
   action wired to the existing outcome column. These columns already
   exist and are currently never set by anything.

4. A basic auth gate (even a single shared password is enough) before
   this is ever run anywhere except localhost.

5. Manual approval required on every send. No code path may send an
   outreach message automatically for the full 30-day test.

Success metric: reply rate and meetings booked from NEXUS-sourced
outreach over 30 days, compared to Faiaz's existing outbound baseline.
Everything else in the original master product document (personas,
pricing tiers, GTM kit, 6-agent architecture, vector RAG) is paused,
not deleted, pending this one result.
```
