# NEXUS Intelligence — API Reference

Base URL: `http://localhost:8000` (dev). All routes below are under `/api/v1`
unless noted. Auth: send `X-Org-Id: <uuid>`; without it, requests resolve to the
seeded demo org (run `python -m app.db.seed` first).

Errors: `401` invalid/missing org, `404` not found, `422` validation,
`503` agent system unavailable.

---

## Ops

### `GET /health`
```json
{"status": "ok"}
```

## Brain

### `POST /brain/onboard`
Ingest business context documents.
```json
// request
{"documents": [{"doc_type": "case_study", "title": "Won: healthtech deal", "content": "..."}]}
// response
{"ingested": 1, "ids": ["<uuid>"]}
```

### `GET /brain/briefing`
Today's daily briefing (generated on first request of the day).
```json
{"id": "<uuid>", "briefing_date": "2026-07-05", "content_markdown": "# Daily Brief..."}
```

### `POST /brain/ask`
Streaming chat. Body `{"question": "Who should I call today?"}`.
Response: `text/event-stream` of `data: <token>` frames ending with `data: [DONE]`.

### `GET /brain/deal/{entry_id}/coach`
Deal coaching for one Action Queue entry.
```json
{"entry_id": "<uuid>", "coaching": "**Deal stand:** ..."}
```

## Intent

### `GET /intent/queue`
Action Queue, strongest score first.
```json
{
  "count": 2,
  "entries": [{
    "id": "<uuid>", "nexus_score": 87,
    "signal_summary": "procurement_notice: Meridian issues RFI... | earnings_language: ...",
    "days_in_window_estimate": 118, "entered_queue_at": "2026-07-05T09:00:00Z",
    "status": "pending",
    "account": {"id": "<uuid>", "company_name": "Meridian Health Systems",
                "domain": "meridianhealth.com", "industry": "healthtech",
                "employee_count": 850, "geography": "United States"},
    "score": {"urgency": 100, "fit": 87, "budget_probability": 100,
              "composite_nexus_score": 87, "explanation": "NEXUS 87/100 = ...",
              "scored_at": "2026-07-05T09:00:00Z"},
    "signals": [ /* up to 5 latest signal objects */ ]
  }]
}
```

### `GET /intent/account/{account_id}`
Full profile: account, latest + historical scores, signal timeline, outreach drafts.

### `POST /intent/outreach/{account_id}`
Generate the 3-variant outreach package.
```json
{"drafts": [{
  "id": "<uuid>", "variant": "assertive",
  "email_subject": "Question about Meridian's next 90 days",
  "email_body": "...", "linkedin_message": "...", "call_script": "...",
  "positioning_frame": "...", "signal_reference": "...",
  "sent_at": null, "outcome": null, "created_at": "..."
}]}
```

### `PUT /intent/icp`
Upsert the org's ICP profile.
```json
// request
{"target_industries": ["saas"], "company_size_min": 50, "company_size_max": 1500,
 "titles_targeted": ["CEO"], "geographies": ["United States"],
 "tech_stack_keywords": ["Salesforce"], "offer_description": "..."}
// response
{"id": "<uuid>", "status": "saved"}
```

### `POST /intent/pipeline/run`
Manually trigger a full supervisor cycle.
```json
{"persisted_signals": 8, "classified_signals": 8, "queued_accounts": 2,
 "human_review": [], "budget_blocked": false}
```

## Signals

### `GET /signals/stream`
Server-sent events. Emits new signals (JSON per `data:` frame) every ~3s poll,
heartbeat comments between.

### `POST /signals/custom`
```json
// request (account_id OR company_name)
{"company_name": "Acme Corp", "signal_type": "leadership_change",
 "title": "Acme appoints new COO", "raw_data": {}}
// response
{"id": "<uuid>", "account_id": "<uuid>", "status": "created"}
```

### `GET /signals/history/{days}`
Signals from the last N days (1-365), newest first.
```json
{"days": 30, "count": 21, "signals": [ /* signal objects */ ]}
```

## Analytics

### `GET /analytics/pipeline`
```json
{"funnel": [
  {"stage": "signals_detected", "count": 21},
  {"stage": "signals_classified", "count": 21},
  {"stage": "accounts_scored", "count": 10},
  {"stage": "accounts_queued", "count": 2},
  {"stage": "outreach_generated", "count": 1},
  {"stage": "contacted", "count": 0},
  {"stage": "replied", "count": 0}
]}
```

### `GET /analytics/signals`
Counts by type and urgency tier over the last 30 days.
```json
{"window_days": 30,
 "by_type": [{"signal_type": "job_post", "count": 6}],
 "by_tier": [{"urgency_tier": "HOT", "count": 5}]}
```

### `GET /analytics/pipeline-events`
Recent pipeline-level audit events (collector failures, budget-exceeded stops).
Per-call LLM routing detail lives in `/analytics/costs` instead. Optional
`?limit=` query param, default 50, max 200.
```json
{"events": [
  {"id": "<uuid>", "event_type": "budget_exceeded",
   "detail": {"stage": "intent_classifier", "error": "..."},
   "created_at": "2026-07-06T09:00:00Z"}
]}
```

### `GET /analytics/costs`
Today's LLM spend, read from OpenRouter's authoritative per-request `usage.cost`
(see `app/core/llm_router.py`), broken down by model and by purpose.
```json
{"total_usd": 0.08,
 "by_model": {"moonshotai/kimi-k2-thinking": 0.08},
 "by_purpose": {"classify": 0.0, "outreach": 0.05, "brain": 0.03},
 "top_model_by_purpose": {"outreach": "moonshotai/kimi-k2-thinking"},
 "fallback_events": [],
 "daily_limit_usd": 0.25,
 "over_budget": false}
```
