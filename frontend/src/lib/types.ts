/**
 * Core domain types for NEXUS INTELLIGENCE.
 * Mirrors backend/app/db/models.py — see docs/CONTRACT.md for canonical strings.
 */

export type SignalType =
  | "job_post"
  | "leadership_change"
  | "funding"
  | "procurement_notice"
  | "earnings_language"
  | "tech_change"
  | "news"
  | "filing";

export type UrgencyTier = "HOT" | "WARM" | "COOL";

export type SignalStatus = "new" | "classified" | "scored" | "archived";

export type QueueStatus =
  | "pending"
  | "outreach_generated"
  | "contacted"
  | "dismissed"
  | "converted";

export type BudgetImplication = "CONFIRMED" | "PROBABLE" | "POSSIBLE" | "NONE";

export type OutreachFrame = "assertive" | "analytical" | "challenger";

export interface Signal {
  id: string;
  accountId: string;
  signalType: SignalType;
  source: string;
  headline: string;
  summary: string;
  urgencyTier: UrgencyTier;
  budgetImplication: BudgetImplication;
  detectedAt: string; // ISO date
  status: SignalStatus;
  daysToActionWindow: number;
}

export interface Account {
  id: string;
  companyName: string;
  domain: string;
  industry: string;
  employeeCount: number;
  revenueEstimate: string;
  geography: string;
  techStack: string[];
  lastEnrichedAt: string;
}

export interface AccountScore {
  accountId: string;
  urgency: number;
  fit: number;
  budgetProbability: number;
  compositeNexusScore: number;
  scoredAt: string;
  explanation: string;
  signalIds: string[];
}

export interface ActionQueueEntry {
  id: string;
  account: Account;
  score: AccountScore;
  signalSummary: string;
  signals: Signal[];
  enteredQueueAt: string;
  status: QueueStatus;
  daysInWindowEstimate: number;
  recommendedContacts: Contact[];
}

export interface Contact {
  id: string;
  name: string;
  title: string;
  linkedinUrl: string;
  email: string;
}

export interface OutreachVariant {
  frame: OutreachFrame;
  emailSubject: string;
  emailBody: string;
  linkedinMessage: string;
  callScript: string;
  positioningNote: string;
}

export interface OutreachDraft {
  id: string;
  accountId: string;
  signalReference: string;
  variants: OutreachVariant[];
  status: "draft" | "sent" | "replied";
  sentAt: string | null;
  replyReceivedAt: string | null;
}

export interface BrainBriefing {
  id: string;
  orgId: string;
  briefingDate: string;
  contentMarkdown: string;
  pinnedAlerts: string[];
}

export interface ICPProfile {
  targetIndustries: string[];
  companySizeMin: number;
  companySizeMax: number;
  titlesTargeted: string[];
  geographies: string[];
  techKeywords: string[];
  offerDescription: string;
}

export interface PipelineFunnelStage {
  stage: "signals" | "scored" | "queued" | "contacted" | "replied";
  label: string;
  count: number;
}

export interface SignalTypeCount {
  signalType: SignalType;
  tier: UrgencyTier;
  count: number;
}

export interface TodayStats {
  newSignals: number;
  queueDepth: number;
  outreachSent: number;
  repliesReceived: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export interface LLMCostSummary {
  totalUsd: number;
  byModel: Record<string, number>;
  byPurpose: Record<string, number>;
  topModelByPurpose: Record<string, string>;
  fallbackEvents: { model: string; purpose: string; reason?: string }[];
  dailyLimitUsd: number;
  overBudget: boolean;
}

export interface PlanUsage {
  planName: "NEXUS Solo" | "NEXUS Agency" | "NEXUS Enterprise" | "NEXUS AI Install";
  accountsMonitored: number;
  accountsLimit: number;
  actionQueueCreditsUsed: number;
  actionQueueCreditsLimit: number | null; // null = unlimited
  seatsUsed: number;
  seatsLimit: number;
  renewsOn: string;
}
