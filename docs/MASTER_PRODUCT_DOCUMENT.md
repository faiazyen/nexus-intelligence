# NEXUS INTELLIGENCE — Master Product Document
### Business Brain + AI Intent Platform | Full Product Bible & Master Claude Prompt
**Compiled by: Virtual World-Class Expert Team | July 2026**

***

> *"The companies that win the next decade will not be the ones with the most salespeople. They will be the ones whose AI knows who is about to buy — before anyone else does."*

***

## PART 1: MARKET INTELLIGENCE BRIEF
*(Senior Strategy Team — McKinsey/BCG Level Analysis)*

### 1.1 The Market Opportunity

The global B2B buyer intent data tools market is valued at **$4.49 billion in 2026**, projected to reach **$20.89 billion by 2035** at a 16.62% CAGR. This is one of the fastest-growing segments in the entire martech stack. Yet despite massive adoption — **91% of B2B marketers now use intent data** to prioritize accounts — only **24% see meaningful ROI**. That gap is the opportunity.[^1][^2]

**The core problem no one has solved:**
- 70%+ of the B2B buying journey happens in the "dark funnel" — invisible to all current tools[^1]
- Existing platforms (Bombora, 6sense, ZoomInfo, Demandbase) charge $5,000–$60,000+/year and are built for enterprise marketing teams[^3][^4]
- The **"signal-to-action gap"** is the industry's biggest unsolved problem — tools show you data but leave you to figure out what to do with it[^5][^6]
- No product serves the $50K–$150K consulting and B2B services market with pre-RFP intelligence at an accessible price point[^7]
- Signal-based outreach achieves **15–25% reply rates** vs 1–5% for generic cold email — yet 90% of companies still send generic outreach[^8]

**The timing asymmetry insight (from the Instagram slides analyzed):**
By the time a company issues an RFP, the decision has already been shaped in a meeting you were not in. Six weeks earlier, a CMO named the problem, Finance approved a budget, and Procurement was told to run a comparison. The winner is the person who was in the room when the problem was first named.

### 1.2 Competitive Landscape

| Competitor | Core Weakness | Price | Who They Serve |
|---|---|---|---|
| **Bombora** | Pure data layer — no activation, no action guidance | $25K+/yr | Enterprise ABM teams[^9] |
| **6sense** | $10K+/month, long onboarding, requires full ABM team | $120K+/yr | Enterprise-only[^3] |
| **ZoomInfo Intent** | Data + contacts but no agentic action layer | $15K+/yr | Mid-market/Enterprise[^4] |
| **Demandbase** | Focused on ad targeting, not pre-RFP origination | $8K+/mo | Enterprise marketing[^3] |
| **Apollo.io** | Contact database, not intelligence — weak signal quality | $99–$599/mo | SMB/Mid-market[^10] |
| **Clay** | Data enrichment tool — no reasoning, no intent prediction | $149–$800/mo | Growth/GTM operators[^11] |
| **Tendor.ai** | Pre-RFP for public sector only, limited B2B coverage | Custom | Govt contractors[^7] |
| **Landbase** | Good signals but no "business brain" reasoning layer | Custom | Enterprise only[^12] |

**The White Space:** No product exists that combines (1) pre-RFP signal intelligence, (2) an agentic "Business Brain" reasoning about *why* a signal matters for *your specific offer*, (3) autonomous outreach generation, and (4) pricing accessible to consultants, agencies, and B2B service firms.[^13][^5]

### 1.3 The Two-Product Vision: NEXUS INTELLIGENCE

**Product 1 — NEXUS BRAIN (Business Intelligence Layer)**
A living, learning AI brain that understands your business, your ICP, your past wins, your competitors, and your market. It ingests your internal knowledge (CRM, proposals, emails, decks) and external market data to become the smartest strategic advisor in the room.[^14][^15]

**Product 2 — NEXUS INTENT (Pre-RFP Signal Intelligence Engine)**
An agentic system that monitors 10,000+ daily signals across public records, filings, job posts, leadership changes, procurement notices, and industry databases — then scores and routes only the highest-intent accounts to your outreach queue with a ready-to-send, context-aware message.[^16][^12]

**The Fusion (NEXUS COMPLETE):**
NEXUS BRAIN + NEXUS INTENT creates something no competitor offers: a system that not only finds the right account at the right time, but knows exactly what to say — because it understands your offer, their trigger, and the gap between what they think they need and what the problem is actually costing them.[^6][^13]

***

## PART 2: PRODUCT SPECIFICATION
*(Senior Product Manager + CTO + Solution Architect)*

### 2.1 System Architecture

```
NEXUS INTELLIGENCE PLATFORM
======================================================
[NEXUS BRAIN]                    [NEXUS INTENT]
Business Knowledge Layer         Pre-RFP Signal Engine
---------------------------      ---------------------------
Business Context Engine  <--->   Signal Collectors (Agents)
  - ICP Profile                    - Job Post Monitor
  - Offer Matrix                   - SEC/13F Filing Watcher
  - Win/Loss DNA                   - Leadership Change Tracker
  - Competitor Map                 - Procurement Notice Scraper
                                   - Budget Signal Detector

Reasoning Engine (Claude) <--->  Signal Fusion & Scoring
  - RAG over business docs         - Urgency Score (0-100)
  - Market synthesis               - Fit Score (0-100)
  - Deal coaching                  - Budget Probability (0-100)

Output Layer              <--->  Action Queue
  - Daily Briefings                - Scored Accounts (≥70)
  - Talk Tracks                    - Signal-Specific Outreach
  - Proposal Drafts                - Meeting Booking
```

### 2.2 NEXUS BRAIN — Feature Specification

| Module | Description | Data Sources |
|---|---|---|
| **Business Context Ingestion** | Onboards your offer, ICP, pricing, past deals, objections | CRM export, proposal docs, email history |
| **Competitor Intelligence** | Tracks competitor moves, pricing changes, positioning shifts | Web scraping, news, G2 reviews |
| **Market Signal Synthesis** | Weekly briefing of what's changing in your target market | Industry news, LinkedIn, Earnings calls |
| **Deal Coaching** | Real-time guidance on open deals — what to say, when to push | CRM + email thread context |
| **Proposal Generator** | Creates first-draft proposals using win patterns from past deals | Past wins + new account data |
| **Objection Playbook** | Living document of every objection ever raised, with winning responses | Email/call transcripts |

**Technical Layer:** Claude Opus 4.x via Anthropic API (Build/Scale tier, rate limits significantly raised in May–June 2026), Qdrant vector DB for RAG, LangGraph for orchestration.[^17][^18][^19][^20]

### 2.3 NEXUS INTENT — Signal Types

| Signal Category | What It Detects | Why It Matters |
|---|---|---|
| **Job Postings** | New roles indicating team build-out or capability gap | Approved budget sitting next to an unsolved problem[^16] |
| **Leadership Changes** | New C-suite, VP, or Director appointments | Every contract the predecessor signed is now under review[^21] |
| **13F & SEC Filings** | Institutional capital movements, M&A filings | Capital moving 4–8 months before vendor spend follows[^21] |
| **Procurement Notices** | Pre-solicitation notices, RFI publications | 4–6 months before the RFP exists[^7][^22] |
| **Earnings Call Language** | Phrases indicating pain or new initiative | "We're investing in X" = active budget allocation[^21] |
| **Funding Announcements** | Seed, Series A/B/C rounds | New CEO mandate to build the GTM machine NOW[^4] |
| **Technology Stack Changes** | BuiltWith, job post tech mentions | Switching vendors = open review window[^23] |
| **News & PR Signals** | New product launches, partnerships, reorgs | Each announcement reshuffles priorities and vendor relationships[^16] |

**NEXUS Score Formula:**

Each account receives a composite score:
- **Urgency Score (0–100):** Signal recency × type weight × concurrent signal count[^16]
- **Fit Score (0–100):** Industry + size + tech stack + geography + title presence match to ICP
- **Budget Probability (0–100):** Job post (+15), funding (+25), new exec (+20), earnings language (+30), pre-solicitation notice (+40)
- **Timing Window:** Leadership change = 90 days; new funding = 60 days; job post = 45 days

Accounts scoring ≥70 on all dimensions are routed to the Action Queue.[^24]

### 2.4 The Differentiation Statement

NEXUS is not an intent data vendor. It is not an SDR tool. It is not a CRM.

NEXUS is the first platform that closes the full loop:[^13][^6]
1. **Monitor** — continuous signal surveillance of 10,000+ triggers per day
2. **Reason** — Claude-powered interpretation through the lens of YOUR specific business
3. **Score** — multi-dimensional ranking by urgency, fit, and timing
4. **Act** — fully drafted, signal-specific outreach ready to send in one click

The key innovation is the **Reasoning Bridge**: most tools give data. NEXUS tells you what it means for your deal, who to contact, what to say, and why *this week* — not next month.[^12][^5]

***

## PART 3: BUSINESS MODEL
*(CEO + CFO + GTM Leader)*

### 3.1 Pricing Architecture

| Tier | Name | Price | Target | Includes |
|---|---|---|---|---|
| **Starter** | NEXUS Solo | $299/month | Freelance consultants, solo B2B operators | 500 accounts monitored, 50 Action Queue credits/mo, NEXUS BRAIN basic |
| **Growth** | NEXUS Agency | $799/month | Agencies, boutique consultancies (2–20 staff) | 2,000 accounts, unlimited Action Queue, NEXUS BRAIN full, 3 team seats |
| **Scale** | NEXUS Enterprise | $2,499/month | Mid-market consulting firms, B2B SaaS GTM teams | 10,000+ accounts, multi-ICP, API access, CRM integration, dedicated CS |
| **Custom** | NEXUS AI Install | Contact | White-glove consulting install | Custom signal types, team training, SLA |

**Revenue Targets:**
- Month 12 ARR: $2.4M (1,000 customers at blended $200 ARPU)
- Month 24 ARR: $12M (5,000 customers, upsell into Enterprise tier)

By comparison, Bombora starts at $25K/year and 6sense at $10K+/month — NEXUS targets the completely underserved segment below that threshold.[^9][^4]

### 3.2 GTM Strategy

**Phase 1 — Nail the Wedge (Months 1–3):**
Target solo consultants and boutique agencies doing $250K–$2M/year in B2B services. Channel: organic LinkedIn content + direct outbound using NEXUS on itself ("we use our own product to find customers"). Goal: 100 paid beta users, NPS > 60, 3 case studies.

**Phase 2 — Climb the Value Chain (Months 4–9):**
Layer in Agency tier, push into B2B SaaS GTM teams. Launch Product Hunt + AppSumo. Partner with Clay, Apollo, and HubSpot as integration partners. Goal: 500 paid customers, MRR $150K.[^25]

**Phase 3 — Enterprise and Scale (Months 10–18):**
Launch native CRM integrations (Salesforce, HubSpot). White-label for top consulting firms. Series A raise target: $8–12M. Goal: 2,000 customers, MRR $500K+.

### 3.3 Defensibility & Moat

1. **Data Network Effect:** Every company using NEXUS feeds signal pattern data back into the scoring model. More users = better predictions. First-mover advantage compounds.[^23]
2. **Business Context Lock-In:** NEXUS BRAIN ingests years of deals, proposals, and playbooks. Switching cost is very high after 90 days.[^15]
3. **Signal Coverage Breadth:** Building scrapers and parsers for 15+ signal types creates a technical moat that takes 18–24 months to replicate.[^16]
4. **Pricing Moat:** At $299/month vs $25K+/year for Bombora, NEXUS serves a completely unaddressed market segment.[^4]

***

## PART 4: TECHNICAL ARCHITECTURE
*(Senior Solution Architect + Senior Software Engineers + AI/ML Team)*

### 4.1 Full-Stack Technology Decisions

```
FRONTEND
  Framework:     Next.js 14 (App Router), TypeScript strict
  Styling:       Tailwind CSS + Shadcn/UI component library
  Animations:    Framer Motion
  Data viz:      Recharts + custom D3 components
  State:         TanStack Query (server) + Zustand (client)
  LLM streams:   Vercel AI SDK

BACKEND
  Runtime:       Python 3.12
  Framework:     FastAPI (async)
  ORM:           SQLAlchemy 2.0 + Alembic migrations
  Queue:         Celery + Redis
  Agents:        LangGraph (multi-agent orchestration)
  LLM:           Anthropic Claude API
                 Opus 4.x → complex reasoning (Brain, Outreach Writer)
                 Sonnet 4.x → bulk processing
                 Haiku 4.x → real-time scoring (cost-efficient)
  Vector DB:     Qdrant (business context embeddings)
  Search:        PostgreSQL full-text + pgvector

INFRASTRUCTURE
  Cloud:         AWS (ECS Fargate + RDS + ElastiCache + S3)
  IaC:           Terraform
  CI/CD:         GitHub Actions
  Monitoring:    Sentry + Datadog
  Auth:          Clerk.dev
  Billing:       Stripe

DATA SOURCES
  Job boards:    LinkedIn Jobs API, Indeed, Greenhouse, Lever
  Filings:       SEC EDGAR API (free, official)
  Procurement:   SAM.gov API + state portals
  News:          NewsAPI + sector RSS feeds
  Enrichment:    Apollo.io + Clearbit
  Funding:       Crunchbase API
```

Anthropic's API rate limits were significantly raised in May and June 2026, with Sonnet and Haiku now matching Opus at every usage tier, making high-volume agentic builds far more cost-effective.[^19][^20]

### 4.2 Multi-Agent Architecture (LangGraph)

```
AGENT 1 — Signal Scout (runs every 6 hours):
  Scrapes: LinkedIn Jobs, Indeed, SEC EDGAR, SAM.gov, NewsAPI, Crunchbase
  Output: Normalized Signal objects → signal_staging DB

AGENT 2 — Intent Classifier (event-driven):
  Uses Claude Haiku (cost-efficient classification)
  Labels: signal_type, urgency_tier (HOT/WARM/COOL), budget implication
  Enriches with Apollo.io company data

AGENT 3 — Account Scorer (nightly):
  NEXUS Score = (Urgency × Fit × Budget_Probability) / 10000
  Routes score ≥ 70 to action_queue

AGENT 4 — Outreach Writer (triggered by queue entry):
  Uses Claude Opus for quality
  Generates: email (3 sentences), LinkedIn (2 sentences), call opener (30 sec)
  Produces 3 variants: assertive / analytical / challenger frame

AGENT 5 — Business Brain (on-demand + daily 7am):
  RAG retrieval from Qdrant (user's ingested documents)
  Synthesizes with current market signals via Claude Opus
  Streams response via Vercel AI SDK

AGENT 6 — Memory Manager (post-reply, post-deal):
  Logs which outreach worked, which signal predicted the conversion
  Updates scoring weights per signal type per vertical

EXECUTIVE ROUTER (supervisor):
  Orchestrates all 6 agents
  Cost guardrail: < $0.50/day per 100-account org
  Routes errors to human review queue
```

This architecture is validated by real-world open-source implementations: the 10-agent market intelligence system open-sourced on Reddit uses the same "compute-then-synthesize" pattern, proving it is more reliable than RAG-loop approaches for multi-source analysis. LangGraph-based 7-agent sales pipelines have also been demonstrated in production achieving 80%+ automation of SDR tasks.[^26][^24]

### 4.3 Database Schema (Core Tables)

```sql
users            (id UUID, email, name, org_id, plan_tier, created_at)
organizations    (id UUID, name, plan, api_credits_remaining, settings JSONB)
icp_profiles     (id UUID, org_id, target_industries TEXT[], company_size_min INT,
                  company_size_max INT, titles_targeted TEXT[], offer_description TEXT)
business_context (id UUID, org_id, doc_type, content TEXT, embedding_id, created_at)
signals          (id UUID, company_id, signal_type, source, raw_data JSONB,
                  urgency_score INT, relevance_score INT, processed_at, status)
accounts         (id UUID, org_id, company_name, domain, industry, employee_count,
                  revenue_estimate, tech_stack JSONB, last_enriched_at)
account_scores   (id UUID, account_id, urgency INT, fit INT, budget_probability INT,
                  composite_nexus_score INT, scored_at, signal_ids JSONB, explanation)
action_queue     (id UUID, account_id, nexus_score INT, signal_summary TEXT,
                  entered_queue_at, status, days_in_window_estimate INT)
outreach_drafts  (id UUID, account_id, email_subject, email_body, linkedin_message,
                  call_script, signal_reference, sent_at, reply_received_at, outcome)
brain_briefings  (id UUID, org_id, briefing_date DATE, content_markdown TEXT)
```

### 4.4 Key API Endpoints

```
POST   /api/v1/brain/onboard          Ingest business context documents
GET    /api/v1/brain/briefing         Get daily business intelligence briefing
POST   /api/v1/brain/ask              Streaming chat with Business Brain
GET    /api/v1/brain/deal/{id}/coach  Get deal coaching for open opportunity

GET    /api/v1/intent/queue           Get today's Action Queue (scored accounts)
GET    /api/v1/intent/account/{id}    Full signal breakdown for one account
POST   /api/v1/intent/outreach/{id}   Generate outreach for account

GET    /api/v1/signals/stream         Server-sent events for real-time signals
GET    /api/v1/analytics/pipeline     Pipeline conversion analytics
```

***

## PART 5: UI/UX DESIGN SPECIFICATION
*(Senior UI/UX Designer + Brand Strategist)*

### 5.1 Design System

**Visual Identity:** NEXUS should feel like **Bloomberg Terminal meets Notion** — serious, data-rich, but frictionless. Dark mode primary. Every pixel serves data. No decorative elements.

**Color Tokens:**
```css
--nexus-bg:      #0A0E1A   /* Deep navy-black — primary background */
--nexus-surface: #111827   /* Dark grey — cards, panels */
--nexus-border:  #1F2937   /* Subtle border */
--nexus-cyan:    #22D3EE   /* Electric cyan — intelligence, primary accent */
--nexus-emerald: #10B981   /* Emerald — positive signals, success */
--nexus-amber:   #F59E0B   /* Amber — medium urgency */
--nexus-red:     #EF4444   /* Red — high urgency, hot accounts */
--nexus-text:    #F9FAFB   /* Primary text */
--nexus-muted:   #9CA3AF   /* Secondary text, labels */
```

**Core UI Principles:**
1. **Actionability First** — every screen leads to one clear next action
2. **Signal Density** — show as much meaningful data as possible without cognitive overload
3. **Progressive Disclosure** — simple on the surface, infinite depth when you click in
4. **Speed Perception** — skeleton loaders, optimistic UI, instant feedback

### 5.2 Core Product Screens

**Command Center Dashboard:**
- Left: Daily NEXUS Score leaderboard (top 10 accounts, sorted by composite score)
- Center: Signal feed with real-time updates (color-coded by urgency)
- Right: Business Brain chat interface with streaming responses
- Top bar: Today's stats (new signals, queue depth, outreach sent, replies received)

**Action Queue Screen:**
- Card-based layout, one card per hot account, sorted by score descending
- Each card: Company, Signal type, Signal summary, NEXUS Score ring (animated), Days in window
- One-click to generate outreach; one-click to dismiss
- Hover reveals full signal detail and recommended contacts

**Business Brain Screen:**
- Split layout: Chat (60% right) + Briefings panel (40% left)
- Left panel: Today's Daily Brief (auto-generated at 7am), pinned market alerts
- Right panel: Streaming Claude chat, pre-loaded with user's business context
- Quick prompts: "Who should I call today?" / "Coach me on the [Acme] deal"

**Account Profile Screen:**
- Header: Company name, logo, industry, size, NEXUS Score ring, location
- Timeline tab: Every signal detected, reverse chronological, with type icons
- Contacts tab: Recommended decision-makers with role, LinkedIn, email
- Outreach tab: All generated messages with sent/replied status

### 5.3 Landing Pages (Persona-Specific)

**Main Landing Page:**
- Hero: *"Know Who's About to Buy. Before Anyone Else Does."*
- Sub: *"NEXUS monitors 10,000+ daily signals and tells you which companies have budget, a problem, and no vendor — before they write the RFP."*
- CTA: "See Your First 10 Hot Accounts Free"

**Persona Page 1 — `/solo` (Solo Consultant):**
- Headline: *"Stop Waiting For Referrals. Start Getting in the Room Before the Meeting."*

**Persona Page 2 — `/agency` (Agency Owner):**
- Headline: *"Your Competitors Are Responding to RFPs You Should Have Originated."*

**Persona Page 3 — `/gtm` (VP Sales / GTM Leader):**
- Headline: *"Your SDRs Are Prospecting Into Yesterday's Intent Data. NEXUS Tells Them Who's Buying Today."*

***

## PART 6: MASTER CLAUDE PROMPT
*(Senior Prompt Engineer — Production-Grade Build Instruction)*

**COPY EVERYTHING BETWEEN THE === MARKERS AND PASTE AS YOUR FIRST MESSAGE TO CLAUDE OPUS 4.x:**

***

```
═══════════════════════════════════════════════════════════════
NEXUS INTELLIGENCE — MASTER BUILD PROMPT v1.0
TARGET MODEL: Claude Opus 4.x (latest available)
TYPE: Full-Stack SaaS Product Build Instruction
═══════════════════════════════════════════════════════════════

## YOUR IDENTITY AND ROLE

You are NEXUS ARCHITECT — a composite super-intelligence combining the
expertise of a world-class product and engineering team:

- Senior Solution Architect (20+ years, enterprise SaaS, distributed systems)
- Senior Full-Stack Engineer (Python/TypeScript/Next.js/FastAPI/PostgreSQL)
- Senior AI/ML Engineer (LLM orchestration, LangGraph, RAG, Anthropic APIs)
- Senior Product Manager (ex-Salesforce, HubSpot, 3 B2B SaaS exits)
- Senior UI/UX Designer (data-rich B2B dashboards, Bloomberg-style UX)
- Senior GTM Strategist (McKinsey Digital, Challenger Sale methodology)
- Senior Prompt Engineer (production agentic systems, Anthropic partner firms)

You are building NEXUS INTELLIGENCE — a B2B pre-RFP signal intelligence
platform. Your output must be production-ready, deployment-grade code
and documentation. Not prototypes. Not pseudocode. The real thing.

---

## THE PRODUCT YOU ARE BUILDING

NEXUS solves this precise problem:

By the time a B2B vendor sees an RFP, the deal is already decided. Six
weeks earlier, a CMO named the problem, Finance approved the budget, and
Procurement was told to run a comparison. The vendor who wins is the one
who was in the room when the problem was first named — 4–8 months before
the RFP exists.

NEXUS makes that timing advantage a system, not luck.

PRODUCT 1 — NEXUS BRAIN:
An AI business intelligence layer that learns your business context (ICP,
offer, past wins, competitors) and becomes your strategic advisor. Powered
by Claude Opus via RAG over ingested business documents. Delivers daily
briefings, deal coaching, proposal drafts, and real-time Q&A.

PRODUCT 2 — NEXUS INTENT:
A multi-agent system that monitors 10,000+ daily signals across public
records, SEC filings, job posts, leadership changes, procurement notices,
earnings calls, and funding data. Scores every account by urgency, ICP
fit, and budget probability. Routes high-score accounts to an Action Queue
with signal-specific outreach ready to send.

---

## TECHNOLOGY STACK (NON-NEGOTIABLE)

Frontend:         Next.js 14 (App Router), TypeScript strict, Tailwind CSS,
                  Shadcn/UI, Framer Motion, Recharts, TanStack Query, Zustand,
                  Vercel AI SDK for LLM streaming

Backend:          Python 3.12, FastAPI (async), SQLAlchemy 2.0, Alembic,
                  Celery + Redis, LangGraph, Anthropic SDK

LLM Tier:         Claude Opus 4.x  → complex reasoning (Brain, Outreach)
                  Claude Sonnet 4.x → bulk processing
                  Claude Haiku 4.x  → real-time scoring, classification

Storage:          PostgreSQL (primary), Redis (cache/queue), Qdrant (vector)

Infrastructure:   AWS ECS Fargate, RDS, ElastiCache, S3
                  Terraform IaC, GitHub Actions CI/CD
                  Clerk.dev (auth), Stripe (billing)

---

## DESIGN SYSTEM

Color palette (apply to ALL UI):
  Background:  #0A0E1A  (deep navy)
  Surface:     #111827  (dark grey cards)
  Cyan:        #22D3EE  (primary accent)
  Emerald:     #10B981  (positive, action)
  Amber:       #F59E0B  (medium urgency)
  Red:         #EF4444  (hot accounts)
  Text:        #F9FAFB  (primary)
  Muted:       #9CA3AF  (secondary)

Feel: Bloomberg Terminal meets Notion. Dark. Data-rich. Precise.

---

## AGENT ARCHITECTURE (6 Agents + 1 Supervisor)

AGENT 1 — Signal Scout (runs every 6 hours):
  Scrapes: LinkedIn Jobs, Indeed, SEC EDGAR, SAM.gov, NewsAPI, Crunchbase
  Output: Normalized Signal objects → signal_staging DB

AGENT 2 — Intent Classifier (event-driven on new signals):
  Uses Claude Haiku for cost-efficient classification
  Labels: signal_type, urgency_tier (HOT/WARM/COOL), budget implication
  Enriches with Apollo.io company data

AGENT 3 — Account Scorer (nightly):
  NEXUS Score = (Urgency × Fit × Budget_Probability) / 10000
  Urgency: signal recency + type weight + concurrent count
  Fit: industry + size + tech stack + geography + title match
  Budget: job_post +15, funding +25, new_exec +20, earnings +30, RFI +40
  Routes score ≥ 70 to action_queue

AGENT 4 — Outreach Writer (triggered by queue entry):
  Uses Claude Opus for quality
  Generates: email (3 sentences), LinkedIn (2 sentences), call opener
  Produces 3 variants: assertive / analytical / challenger frame
  Never pitches product in first touch; always references specific signal

AGENT 5 — Business Brain (on-demand + daily 7am):
  RAG retrieval from Qdrant (user's ingested business documents)
  Synthesizes with current market signals via Claude Opus
  Streaming response via Vercel AI SDK

AGENT 6 — Memory Manager (post-reply, post-deal):
  Logs which outreach worked, which signal predicted the conversion
  Updates scoring weights; maintains rolling win DNA per org

EXECUTIVE ROUTER (supervisor):
  Orchestrates all 6 agents via LangGraph
  Cost guardrail: < $0.50/day per 100-account org
  Use Haiku for all classification; Opus only for Brain + Outreach

---

## BUILD SEQUENCE

Execute phases in order. Complete each fully before advancing.
End each phase with: ✅ PHASE COMPLETE — [list of all files created]

PHASE 1: PROJECT SCAFFOLDING
  Create the full project tree with all files initialized.
  nexus-intelligence/
  ├── frontend/   (Next.js 14 — all pages, layouts, components)
  ├── backend/    (FastAPI — all routers, agents, models, services)
  └── infrastructure/ (Terraform, Docker, CI/CD)

PHASE 2: DATABASE SCHEMA
  All SQLAlchemy models + Alembic migration (revision 001_initial)
  Tables: users, organizations, icp_profiles, business_context_docs,
          signals, accounts, account_scores, action_queue,
          outreach_drafts, brain_conversations, brain_briefings
  Seed script: 10 sample accounts + 20 sample signals

PHASE 3: BACKEND API — ALL ROUTERS (full implementation, not stubs)
  brain.py:     POST /onboard, GET /briefing, POST /ask, GET /deal/{id}/coach
  intent.py:    GET /queue, GET /account/{id}, POST /outreach/{id}, PUT /icp
  signals.py:   GET /stream (SSE), POST /custom, GET /history/{days}
  analytics.py: GET /pipeline, GET /signals

PHASE 4: AGENT SYSTEM — ALL 6 AGENTS
  Each agent: LangGraph StateGraph, all nodes, edge logic, tool definitions
  System prompts for all LLM nodes
  Unit tests for each agent state transition

PHASE 5: SCORING ENGINE
  Full compute_nexus_score() with all sub-functions
  Unit tests with synthetic signal data covering all signal types

PHASE 6: OUTREACH GENERATION
  Full Outreach Writer Agent
  3-variant output (assertive / analytical / challenger)
  Quality filters: no generic openers, must reference specific signal,
                   email body max 3 sentences

PHASE 7: FRONTEND — ALL PAGES (full implementation)
  Marketing: / (main landing), /solo, /agency, /gtm (full copy + sections)
  Dashboard: command center, action queue, brain chat, account profile,
             signal feed, settings, onboarding flow (6 steps)
  All components: NexusScoreCard, SignalFeed, BrainChat, ActionQueue,
                  AccountProfile, OnboardingFlow

PHASE 8: TESTING SUITE
  Backend: pytest unit + integration tests (80%+ coverage on business logic)
  Frontend: React Testing Library + Playwright E2E
  CI: all tests run on every PR via GitHub Actions

PHASE 9: DEPLOYMENT CONFIG
  docker-compose.yml (local dev, all services)
  docker-compose.prod.yml (production hardened)
  terraform/main.tf (AWS ECS + RDS + ElastiCache + S3)
  .github/workflows/deploy.yml (test → build → push → deploy)
  Dockerfiles (multi-stage, optimized)
  docs/architecture.md + docs/api-reference.md

PHASE 10: GTM LAUNCH PACKAGE
  Product Hunt: tagline + description + first comment
  4-email cold outreach sequence (NEXUS uses to find own customers)
  30-day LinkedIn content calendar
  Investor one-pager (market, problem, solution, traction, ask)

---

## SYSTEM PROMPTS (IMPLEMENT EXACTLY AS WRITTEN)

### Brain Agent System Prompt:
You are the NEXUS Business Brain — a strategic intelligence advisor with
deep expertise in the user's specific business, market, and ICP. You have
been loaded with their business context: past proposals, case studies,
competitor analysis, pricing, and win/loss history.

Your role: help them identify highest-value opportunities TODAY, understand
what's changing in their target market, navigate open deals with tactical
precision, and draft proposals and outreach that win.

Rules:
- Always ground answers in the user's actual business context (from RAG)
- When referencing accounts, always include the NEXUS Score and why it's high
- Be direct. Be specific. No hedging, no vague advice.
- Format for scanning: bold, bullets, headers
- Tone: senior partner at a top consulting firm, talking to a trusted client

### Outreach Writer System Prompt:
You are an elite B2B outreach strategist who has closed $50M+ in
consulting and services contracts. You write outreach that gets responses
because it references the exact moment the prospect is living through.

Outreach philosophy:
1. Reference the SPECIFIC signal — never generic pain points
2. Connect the signal to a cost or risk incurred RIGHT NOW
3. Position sender as the first person to identify the problem
4. Ask is small and specific — a 15-minute conversation, not a pitch
5. NEVER mention the product or service in the first message
6. NEVER use: "hope this finds you well", "circling back", "touching base",
   "synergy", "leverage", "value-add"

For each account, generate:
1. EMAIL SUBJECT: 7 words max. Specific. Not clickbait.
2. EMAIL BODY: Exactly 3 sentences: signal reference → cost framing → ask
3. LINKEDIN MESSAGE: Maximum 2 sentences. Direct. Personal.
4. CALL OPENER: 30 seconds. Context + question. No pitch.
5. POSITIONING FRAME: Internal note — why signal = opportunity for sender.

### Signal Classifier System Prompt:
You are a B2B procurement intelligence analyst. Classify the signal and
extract structured data. Be precise. Return JSON:
{
  "signal_type": "job_post|leadership_change|funding|procurement_notice|
                  earnings_language|tech_change|news|filing",
  "urgency_tier": "HOT|WARM|COOL",
  "budget_implication": "CONFIRMED|PROBABLE|POSSIBLE|NONE",
  "decision_maker_involved": boolean,
  "days_to_action_window": integer,
  "summary": "1 sentence: what this signal means for a B2B vendor"
}

---

## OUTPUT STANDARDS (MANDATORY)

Every code file must:
✅ Be production-ready — no TODOs, no pass statements in core paths
✅ Include try/except with meaningful error messages
✅ Include type annotations (TypeScript strict / Python type hints)
✅ Include docstrings on all non-trivial functions
✅ Be immediately runnable: docker-compose up --build

Every Claude API call must:
✅ Use async/await
✅ Include retry with exponential backoff (3 attempts, 1s/2s/4s)
✅ Log token usage for cost tracking
✅ Have a fallback response when API is unavailable
✅ Use correct model tier (Opus for reasoning, Haiku for classification)

Every UI component must:
✅ Handle loading (skeleton), error (inline), and empty states
✅ Be fully responsive: 375px → 768px → 1440px
✅ Use NEXUS design tokens defined above
✅ Be accessible (WCAG 2.1 AA)

Cost guardrail:
✅ Standard org (100 accounts) must NOT exceed $0.50/day in Claude costs
   - Haiku for all classification tasks
   - Sonnet: max 20 batch calls/day per org
   - Opus: only Brain Q&A and Outreach (demand-driven, not scheduled)

---

## BEGIN BUILD

Start with Phase 1. Output every file in full — never truncate with
"..." or "// rest of file here". Output long files in sequential messages.

After Phase 10, output:
NEXUS LAUNCH CHECKLIST — all 10 phases complete with total file count.

You are the best technical team in the world working on the most
important product of your career. Build accordingly.

═══════════════════════════════════════════════════════════════
END MASTER PROMPT
═══════════════════════════════════════════════════════════════
```

***

## PART 7: TEAM CHARTER & RESPONSIBILITIES

| Role | Key Responsibilities | Deliverables |
|---|---|---|
| **CEO / Vision Lead** | Product-market fit, fundraising, GTM narrative | Business model, investor pitch, brand positioning |
| **CTO** | Technical architecture, engineering culture, security | System design, tech stack, deployment pipeline |
| **Solution Architect** | Infrastructure design, API contracts, scalability | Architecture diagram, API spec, data models |
| **Senior AI/ML Engineer** | Agent design, LLM prompts, RAG pipeline, scoring | Multi-agent system, scoring engine, Claude integration |
| **Senior Full-Stack Engineer** | Frontend + Backend implementation | All code across all phases |
| **Senior Product Manager** | Roadmap, user stories, sprint planning, GTM | PRD, sprint plan, acceptance criteria, launch checklist |
| **Senior UI/UX Designer** | Design system, all screens, all landing pages | Figma file, component library, persona landing pages |
| **Senior Prompt Engineer** | Master prompt architecture, all agent system prompts | Master prompt (Part 6), prompt QA framework |
| **GTM Lead** | Customer acquisition, content, partnerships | Email sequences, LinkedIn calendar, partnerships |

***

## PART 8: MVP LAUNCH CHECKLIST

### Pre-Launch (Weeks 1–4)
- [ ] Docker-compose running locally (all services healthy)
- [ ] Database schema deployed, migrations clean
- [ ] 3 signal types live (job posts, leadership changes, news)
- [ ] Basic NEXUS Score returning results
- [ ] Outreach generation working for all 3 signal types
- [ ] Dashboard displaying real data (not mock)
- [ ] 10 beta users onboarded with real business context
- [ ] Business Brain answering questions from user context

### Soft Launch (Weeks 5–8)
- [ ] All 8 signal types live and running
- [ ] Scoring engine calibrated on beta feedback
- [ ] Action Queue UX tested and NPS > 50
- [ ] All landing pages live with analytics (PostHog)
- [ ] Stripe billing integrated and processing payments
- [ ] 50 paying beta customers
- [ ] 3 case studies documented with pipeline numbers

### Public Launch (Weeks 9–12)
- [ ] Product Hunt launch assets prepared
- [ ] LinkedIn content calendar running (10 posts live)
- [ ] 100 paying customers (MRR ≥ $20K)
- [ ] NPS ≥ 60
- [ ] Series A metrics dashboard built
- [ ] Investor intro emails sent to 50 target funds

***

## APPENDIX A: Open-Source GitHub Building Blocks

| Repository | Owner | Use Case |
|---|---|---|
| b2b-sdr-agent-template | iPythoning | Base SDR agent architecture[^27] |
| Knotie-AI | avijeett007 | Open-source sales agent reference[^28] |
| AI-Powered-RFP-Analyzer | aadrikasingh | RFP processing patterns[^29] |
| Sales-Multi-Agent-AI | RaviKunapareddy | LangGraph agent patterns[^30] |
| autonomous-rfp-agent | aniket-work | RFP automation workflow[^31] |
| ai-crm-agents | KlementMultiverse | 6-agent CRM architecture[^32] |
| Agentic-AI-Pipeline | hoangsonww | Production agent deployment[^33] |
| openrfps-scrapers | dobtco | Government RFP data collection[^34] |
| brightdata/ai-sdr-bdr-agent | brightdata | Trigger detection + CRM integration[^35] |
| ai-community-intelligence | shay | 10-agent market signal system[^26] |

***

## APPENDIX B: Investor Pitch Statistics

| Metric | Value | Source |
|---|---|---|
| B2B intent market 2026 | $4.49 billion | Roots Analysis[^2] |
| Projected market 2035 | $20.89B (16.62% CAGR) | Roots Analysis[^2] |
| Marketers using intent data | 91% | DemandScience 2026[^36] |
| Seeing meaningful ROI | 24% | Derrick App 2026[^1] |
| Signal-based reply rates | 15–25% (vs 1–5% generic) | SalesMotion 2026[^8] |
| Signal GTM pipeline lift | 2.4x higher conversion | GrowthSpree 2026[^37] |
| Sales cycle reduction | 41% shorter | GrowthSpree 2026[^37] |
| Agentic AI adoption (B2B) | 76% deploying or implementing | RevSure 2026[^38] |
| Want full-funnel AI context | 96% believe it improves execution | RevSure 2026[^38] |
| Signal-to-action gap | Core unsolved problem in $4.5B market | Enginy/Landbase 2026[^5][^6] |

***

*NEXUS INTELLIGENCE Master Product Document — Version 1.0*
*Prepared by Virtual Expert Team | July 2026*
*Confidential — For Internal Development Use*

---

## References

1. [B2B Intent Data 2026: The Signal-to-Pipeline Gap](https://derrick-app.com/b2b-intent-data/b2b-intent-data-report-2026) - B2B intent data report 2026: the $4.5B market, 91% use it but only 24% see ROI, the 70% dark funnel,...

2. [B2B Buyer Intent Data Tools Market Size & Trends Report, 2035](https://www.rootsanalysis.com/b2b-buyer-intent-data-tools-market) - The global B2B buyer intent data tools market will grow from USD 4.49 billion in 2026 to USD 20.89 b...

3. [What Are Top Buyer Intent Tools 2026 - BizAI](https://bizaigpt.com/blog/what-are-top-buyer-intent-platforms-2026) - Explore top buyer intent tools 2026: 6sense, Demandbase features, US coverage, pricing & ROI. Predic...

4. [Best Buying Intent Data Tools in 2026 Blog | SyncGTM](https://syncgtm.com/blog/best-buying-intent-data-tools-2026) - Compare the 5 best buying intent data tools in 2026 -- SyncGTM, Bombora, 6sense, ZoomInfo Intent, G2...

5. [The 10 Best Intent Signal Tools for B2B Sales - Enginy](https://www.enginy.ai/blog/intent-signals) - These are the best intent signal tools in 2026: Enginy. Bombora. 6sense. ZoomInfo. Demandbase One. U...

6. [Best B2B Buying Signal Tools for Sales Teams [2026] - MarketBetter](https://www.marketbetter.ai/blog/best-buying-signal-tools-2026/) - Buying signal platforms ranked by signal type, data freshness, and real pricing. Includes numbers mo...

7. [Pre-RFP Signals - Tendor.ai](https://tendor.ai/products/pre-rfp-signals) - Read council minutes, budgets and disclosed capex the day they publish — an early-warning pipeline m...

8. [B2B Prospecting in 2026: The Signal-Based Framework ...](https://salesmotion.io/blog/b2b-prospecting-guide) - Signal-based outreach achieves 15-25% reply rates compared to 1-5% for generic cold email. The key s...

9. [12 best buyer intent data providers for 2026](https://www.guideflow.com/blog/buyer-intent-data-providers) - Buyer intent data providers reveal which companies are researching products like yours. Compare 15 t...

10. [8. Clearbit (hubspot Breeze)](https://www.lusha.com/blog/best-buyer-intent-data-providers/) - Looking for the best buyer intent data provider? We compared 10 tools on signal quality, contact cov...

11. [Best Clay Alternatives 2026: GTM Tools That Go Beyond Enrichment](https://www.miniloop.ai/blog/clay-alternative) - Weaknesses: 6sense is a significant platform investment. Implementation takes time, requires alignme...

12. [Best Tools for Buyer Signal Tracking in 2026 | Landbase](https://www.landbase.com/blog/best-tools-buyer-signal-tracking) - A comprehensive breakdown of the 10 best buyer signal tracking tools in 2026, comparing signal cover...

13. [The 2026 State of Agentic AI in B2B GTM | RevSure](https://revsure.ai/state-of-agentic-ai-b2b-gtm-2026) - Why Agentic AI isn’t delivering at scale for GTM teams. Explore adoption gaps, governance challenges...

14. [The Best 10 AI-Powered Knowledge Base Tools for Teams ...](https://buildin.ai/blog/best-ai-powered-knowledge-base-tools) - Buildin stands as the definitive leader in the 2026 knowledge management landscape. specifically des...

15. [Best Knowledge Management Software in 2026 (AI-Native)](https://www.iwoszapar.com/p/best-knowledge-management-software) - This guide covers seven knowledge management tools judged through an AI-native lens: built-in AI sea...

16. [Automated AI B2B Lead Intelligence & Multi-Channel Outreach Swarm](https://dailyaiworld.com/workflow/ai-lead-intelligence-outreach-swarm)

17. [Claude Code + Agenticflow CLI #2: Build a Lead Qualifier Agent](https://www.youtube.com/watch?v=cgN5IrkXgZ4) - Episode #2 of "Build Agents/Workflows in Minutes: Claude Code + AgenticFlow CLI".

Build a single Ag...

18. [code-forge-temple/agentic-signal: 🤖 Visual AI ...](https://github.com/code-forge-temple/agentic-signal) - Transform complex tasks into visual workflows with local AI intelligence. Connect data sources, AI p...

19. [Anthropic rolls out higher Claude usage limits after SpaceX compute deal- Moneycontrol.com](https://www.moneycontrol.com/artificial-intelligence/anthropic-rolls-out-higher-claude-usage-limits-after-spacex-compute-deal-article-13911076.html) - Anthropic is rolling out higher usage limits for Claude Code and Claude API as rivalry intensifies w...

20. [Anthropic Raises Claude API Rate Limits for QA Agents](https://qatechtools.com/2026/06/29/anthropic-claude-api-rate-limits-qa-agents/amp/) - Anthropic raised Claude API rate limits on June 26, 2026. Here is what QA teams running AI test agen...

21. [How to Detect Software RFP Signals Before the Formal Request](https://salesmotion.io/blog/rfp-request-signals) - 1. Executive Leadership Changes · 2. Strategic Departmental Hiring · 3. Earnings Call Disclosures · ...

22. [Govwin Iq (deltek): Best For...](https://blogs.civiciq.com/2026/04/29/best-government-rfp-tools-software-for-2026-6-platforms-compared/) - FROM CIVIC IQ Stop chasing RFPs your competitors already knew about. Civic IQ monitors 79,000+ gover...

23. [The Best Purchase Intent Data Platforms for 2026](https://www.marketsizer.io/blog/best-purchase-intent-data-platforms-for-2026) - 24+ purchase intent platforms compared by category - evidence-based, aggregated signal, inferred int...

24. [I Built a 7-Agent Sales Pipeline and the Hardest Part Was the Topology](https://dev.to/babulu/i-built-a-7-agent-sales-pipeline-and-the-hardest-part-was-the-topology-2i81) - When I started designing VORTEX — a seven-agent pipeline that turns product usage signals into sales...

25. [AI Sales and GTM Platforms Compared | Ry Walker Research](https://rywalker.com/research/ai-sales-gtm-platforms) - Category analysis of 9 AI-native sales and GTM platforms replacing legacy CRM and outbound tools. Co...

26. [Open-sourced a 10-agent intelligence system that cross-references community, code, research, and hiring data to detect market signals](https://www.reddit.com/r/AI_Agents/comments/1s457vk/opensourced_a_10agent_intelligence_system_that/) - Open-sourced a 10-agent intelligence system that cross-references community, code, research, and hir...

27. [iPythoning/b2b-sdr-agent-template - GitHub](https://github.com/iPythoning/b2b-sdr-agent-template) - An open-source, production-ready template for building AI Sales Development Representatives (SDRs) t...

28. [GitHub - avijeett007/Knotie-AI: Knotie-AI - A Completely Open-Source Inbound/Outbound AI Sales Agent which can communicate with your potential lead/customer.](https://github.com/avijeett007/Knotie-AI) - Knotie-AI - A Completely Open-Source Inbound/Outbound AI Sales Agent which can communicate with your...

29. [aadrikasingh/AI-Powered-RFP-Analyzer - GitHub](https://github.com/aadrikasingh/AI-Powered-RFP-Analyzer) - A turnkey, multi-agent solution accelerator for automating the evaluation of RFPs/RFTs and Vendor/Su...

30. [Multi-Agent AI for Sales Engagement (LangGraph + Gemini) - GitHub](https://github.com/RaviKunapareddy/Sales-Multi-Agent-AI) - A modular, reasoning-first AI pipeline where five specialized agents collaborate to simulate an outb...

31. [Autonomous RFP Response System - A Multi-Agent AI PoC](https://github.com/aniket-work/autonomous-rfp-agent) - The Autonomous RFP Response System is a proof-of-concept (PoC) designed to simulate the workflow of ...

32. [KlementMultiverse/ai-crm-agents: Production-ready AI-powered ...](https://github.com/KlementMultiverse/ai-crm-agents) - Production-ready AI-powered CRM with 6 autonomous agents for lead qualification, email intelligence,...

33. [GitHub - hoangsonww/Agentic-AI-Pipeline: 🦾 A production‑ready research outreach AI agent that plans, discovers, reasons, uses tools, auto‑builds cited briefings, and drafts tailored emails with tool‑chaining, memory, tests, and turnkey Docker, AWS, Ansible & Terraform deploys. Bonus: Agentic RAG system (FAISS + Google CSE) with multistep planning, self-critique, and autonomous agents.](https://github.com/hoangsonww/Agentic-AI-Pipeline) - 🦾 A production‑ready research outreach AI agent that plans, discovers, reasons, uses tools, auto‑bui...

34. [GitHub - dobtco/openrfps-scrapers: Scraping government contracting opportunities.](https://github.com/dobtco/openrfps-scrapers) - Scraping government contracting opportunities. Contribute to dobtco/openrfps-scrapers development by...

35. [GitHub - brightdata/ai-sdr-bdr-agent](https://github.com/brightdata/ai-sdr-bdr-agent) - AI-powered BDR/SDR system that automates lead discovery, trigger detection, contact research, person...

36. [Buyer Intent Data By The...](https://www.omnibound.ai/blog/buyer-intent-data-statistics) - Discover key insights on buyer intent data trends, challenges, and its impact on B2B marketing strat...

37. [Signal-Based GTM Playbook for B2B SaaS and B2B in 2026](https://www.growthspreeofficial.com/blogs/signal-based-gtm-playbook-b2b-saas-b2b-2026-mql-replacement-framework)

38. [Agentic AI Adoption Rises in B2B GTM: 76% of Orgs ...](https://www.linkedin.com/posts/georgetouryliov_the-2026-state-of-agentic-ai-in-b2b-gtm-activity-7421164435047641088-jFTd) - RevSure AI has published "The 2026 State of Agentic AI in B2B GTM" report, based on insights from Se...

