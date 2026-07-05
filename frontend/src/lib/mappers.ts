/**
 * Response mappers: live backend JSON (snake_case, see docs/api-reference.md)
 * -> frontend domain types (camelCase, ./types.ts).
 *
 * Every mapper is defensive: missing/null fields get sensible defaults so a
 * partially-populated backend row can never crash a page.
 */
import type {
  Account,
  AccountScore,
  ActionQueueEntry,
  BrainBriefing,
  ICPProfile,
  LLMCostSummary,
  OutreachDraft,
  OutreachFrame,
  OutreachVariant,
  PipelineFunnelStage,
  QueueStatus,
  Signal,
  SignalType,
  UrgencyTier,
} from "./types";

type Raw = Record<string, any>;

export function mapSignal(raw: Raw): Signal {
  return {
    id: String(raw.id ?? ""),
    accountId: String(raw.account_id ?? ""),
    signalType: (raw.signal_type ?? "news") as SignalType,
    source: String(raw.source ?? ""),
    headline: String(raw.title ?? raw.headline ?? ""),
    summary: String(raw.summary ?? ""),
    urgencyTier: (raw.urgency_tier ?? "COOL") as UrgencyTier,
    budgetImplication: raw.budget_implication ?? "NONE",
    detectedAt: String(raw.detected_at ?? new Date().toISOString()),
    status: raw.status ?? "new",
    daysToActionWindow: Number(raw.days_to_action_window ?? 30),
  };
}

export function mapAccount(raw: Raw): Account {
  return {
    id: String(raw.id ?? ""),
    companyName: String(raw.company_name ?? "Unknown company"),
    domain: String(raw.domain ?? ""),
    industry: String(raw.industry ?? ""),
    employeeCount: Number(raw.employee_count ?? 0),
    revenueEstimate: raw.revenue_estimate ? `$${Number(raw.revenue_estimate).toLocaleString()}` : "",
    geography: String(raw.geography ?? ""),
    techStack: raw.tech_stack ? Object.values(raw.tech_stack).map(String) : [],
    lastEnrichedAt: String(raw.last_enriched_at ?? ""),
  };
}

export function mapScore(raw: Raw | null | undefined, accountId: string): AccountScore {
  return {
    accountId,
    urgency: Number(raw?.urgency ?? 0),
    fit: Number(raw?.fit ?? 0),
    budgetProbability: Number(raw?.budget_probability ?? 0),
    compositeNexusScore: Number(raw?.composite_nexus_score ?? 0),
    scoredAt: String(raw?.scored_at ?? new Date().toISOString()),
    explanation: String(raw?.explanation ?? ""),
    signalIds: Array.isArray(raw?.signal_ids) ? raw.signal_ids.map(String) : [],
  };
}

export function mapQueueEntry(raw: Raw): ActionQueueEntry {
  const account = mapAccount(raw.account ?? {});
  return {
    id: String(raw.id ?? ""),
    account,
    score: mapScore(raw.score, account.id),
    signalSummary: String(raw.signal_summary ?? ""),
    signals: Array.isArray(raw.signals) ? raw.signals.map(mapSignal) : [],
    enteredQueueAt: String(raw.entered_queue_at ?? new Date().toISOString()),
    status: (raw.status ?? "pending") as QueueStatus,
    daysInWindowEstimate: Number(raw.days_in_window_estimate ?? 30),
    recommendedContacts: [],
  };
}

export function mapQueueResponse(raw: Raw): ActionQueueEntry[] {
  const entries = Array.isArray(raw?.entries) ? raw.entries : Array.isArray(raw) ? raw : [];
  return entries.map(mapQueueEntry);
}

function draftsToVariants(drafts: Raw[]): OutreachVariant[] {
  return drafts.map((draft) => ({
    frame: (draft.variant ?? "analytical") as OutreachFrame,
    emailSubject: String(draft.email_subject ?? ""),
    emailBody: String(draft.email_body ?? ""),
    linkedinMessage: String(draft.linkedin_message ?? ""),
    callScript: String(draft.call_script ?? ""),
    positioningNote: String(draft.positioning_frame ?? ""),
  }));
}

export function mapAccountProfileResponse(raw: Raw): {
  account: Account;
  signals: Signal[];
  entry?: ActionQueueEntry;
  outreachDraft?: OutreachDraft;
} {
  const account = mapAccount(raw.account ?? {});
  const signals = Array.isArray(raw.signals) ? raw.signals.map(mapSignal) : [];
  const latest = raw.latest_score;
  const entry: ActionQueueEntry | undefined = latest
    ? {
        id: account.id,
        account,
        score: mapScore(latest, account.id),
        signalSummary: String(latest.explanation ?? ""),
        signals,
        enteredQueueAt: String(latest.scored_at ?? new Date().toISOString()),
        status: "pending",
        daysInWindowEstimate: 30,
        recommendedContacts: [],
      }
    : undefined;

  // outreach_drafts is ordered newest-first and generate_outreach_for_account
  // always creates exactly one row per variant in the same call, so the
  // front of the list is one complete 3-variant batch from the most recent
  // generation. Surfacing it here means a page reload doesn't lose
  // previously-generated outreach the way relying only on the mutation's
  // in-memory result would.
  const rawDrafts: Raw[] = Array.isArray(raw.outreach_drafts) ? raw.outreach_drafts : [];
  const firstDraft = rawDrafts[0];
  const outreachDraft: OutreachDraft | undefined = firstDraft
    ? {
        id: String(firstDraft.id ?? `persisted-${account.id}`),
        accountId: account.id,
        signalReference: String(firstDraft.signal_reference ?? ""),
        variants: draftsToVariants(rawDrafts.slice(0, 3)),
        status: firstDraft.sent_at ? "sent" : "draft",
        sentAt: firstDraft.sent_at ?? null,
        replyReceivedAt: firstDraft.reply_received_at ?? null,
      }
    : undefined;

  return { account, signals, entry, outreachDraft };
}

export function mapOutreachResponse(raw: Raw, accountId: string): OutreachDraft {
  const drafts: Raw[] = Array.isArray(raw?.drafts) ? raw.drafts : [];
  const variants: OutreachVariant[] = draftsToVariants(drafts);
  return {
    id: String(drafts[0]?.id ?? `live-${accountId}`),
    accountId,
    signalReference: String(drafts[0]?.signal_reference ?? ""),
    variants,
    status: "draft",
    sentAt: null,
    replyReceivedAt: null,
  };
}

export function mapBriefingResponse(raw: Raw): BrainBriefing {
  return {
    id: String(raw.id ?? ""),
    orgId: String(raw.org_id ?? ""),
    briefingDate: String(raw.briefing_date ?? new Date().toISOString().slice(0, 10)),
    contentMarkdown: String(raw.content_markdown ?? ""),
    pinnedAlerts: [],
  };
}

export function mapSignalsHistoryResponse(raw: Raw): Signal[] {
  const signals = Array.isArray(raw?.signals) ? raw.signals : Array.isArray(raw) ? raw : [];
  return signals.map(mapSignal);
}

const FUNNEL_STAGE_MAP: Record<string, { stage: PipelineFunnelStage["stage"]; label: string }> = {
  signals_detected: { stage: "signals", label: "Signals detected" },
  accounts_scored: { stage: "scored", label: "Accounts scored" },
  accounts_queued: { stage: "queued", label: "Queued (70+)" },
  contacted: { stage: "contacted", label: "Contacted" },
  replied: { stage: "replied", label: "Replied" },
};

export function mapPipelineResponse(raw: Raw): PipelineFunnelStage[] {
  const funnel: Raw[] = Array.isArray(raw?.funnel) ? raw.funnel : [];
  const stages: PipelineFunnelStage[] = [];
  for (const item of funnel) {
    const mapped = FUNNEL_STAGE_MAP[String(item.stage)];
    if (mapped) {
      stages.push({ ...mapped, count: Number(item.count ?? 0) });
    }
  }
  return stages;
}

// The ICP endpoints are the one place the frontend's ICPProfile type
// (camelCase) and the backend's wire format (snake_case, see ICPRequest in
// intent.py) actually differ in field naming rather than just structure.
// Every other endpoint already goes through a mapper; ICP originally didn't,
// which meant PUT silently sent camelCase keys the backend's Pydantic model
// couldn't match, saving nothing but defaults. Route both directions through
// these two functions instead of hand-rolling the conversion at each call site.

export function mapICPFromWire(raw: Raw): ICPProfile {
  return {
    targetIndustries: Array.isArray(raw.target_industries) ? raw.target_industries : [],
    companySizeMin: Number(raw.company_size_min ?? 10),
    companySizeMax: Number(raw.company_size_max ?? 1000),
    titlesTargeted: Array.isArray(raw.titles_targeted) ? raw.titles_targeted : [],
    geographies: Array.isArray(raw.geographies) ? raw.geographies : [],
    techKeywords: Array.isArray(raw.tech_stack_keywords) ? raw.tech_stack_keywords : [],
    offerDescription: String(raw.offer_description ?? ""),
  };
}

export function mapICPToWire(profile: ICPProfile): Raw {
  return {
    target_industries: profile.targetIndustries,
    company_size_min: profile.companySizeMin,
    company_size_max: profile.companySizeMax,
    titles_targeted: profile.titlesTargeted,
    geographies: profile.geographies,
    tech_stack_keywords: profile.techKeywords,
    offer_description: profile.offerDescription,
  };
}

export function mapCostSummary(raw: Raw): LLMCostSummary {
  const fallbackEvents: Raw[] = Array.isArray(raw.fallback_events) ? raw.fallback_events : [];
  return {
    totalUsd: Number(raw.total_usd ?? 0),
    byModel: raw.by_model && typeof raw.by_model === "object" ? raw.by_model : {},
    byPurpose: raw.by_purpose && typeof raw.by_purpose === "object" ? raw.by_purpose : {},
    topModelByPurpose:
      raw.top_model_by_purpose && typeof raw.top_model_by_purpose === "object"
        ? raw.top_model_by_purpose
        : {},
    fallbackEvents: fallbackEvents.map((e) => ({
      model: String(e.model ?? ""),
      purpose: String(e.purpose ?? ""),
      reason: e.reason ? String(e.reason) : undefined,
    })),
    dailyLimitUsd: Number(raw.daily_limit_usd ?? 0.25),
    overBudget: Boolean(raw.over_budget),
  };
}
