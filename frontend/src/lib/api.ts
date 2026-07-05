/**
 * Typed API client for NEXUS INTELLIGENCE.
 *
 * Every hook here reads from process.env.NEXT_PUBLIC_API_URL and falls back
 * to bundled demo fixtures (./demo-data.ts) whenever the backend is
 * unreachable, unresponsive, or returns a non-2xx status. This lets the
 * frontend demo standalone with zero backend running.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type {
  ActionQueueEntry,
  Account,
  BrainBriefing,
  ICPProfile,
  OutreachDraft,
  PipelineFunnelStage,
  Signal,
  SignalTypeCount,
  TodayStats,
} from "./types";
import {
  demoAccounts,
  demoActionQueue,
  demoBriefing,
  demoICP,
  demoPipeline,
  demoPlanUsage,
  demoSignalCounts,
  demoSignals,
  demoTodayStats,
  buildDemoOutreach,
} from "./demo-data";
import {
  mapAccountProfileResponse,
  mapBriefingResponse,
  mapICPFromWire,
  mapICPToWire,
  mapOutreachResponse,
  mapPipelineResponse,
  mapQueueResponse,
  mapSignal,
  mapSignalsHistoryResponse,
} from "./mappers";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

// No auth/org-selection UI exists yet, so no real org id is available on the
// client. Omitting X-Org-Id lets the backend's own get_current_org dependency
// fall back to the seeded demo org (see backend/app/routers/deps.py) — the
// same fallback the SSE stream already relies on implicitly, since
// EventSource cannot set custom request headers at all. Sending a made-up
// placeholder UUID here would only cause a 404 on every live request.
const FETCH_TIMEOUT_MS = 5000;

class ApiUnavailableError extends Error {}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
    if (!res.ok) {
      throw new ApiUnavailableError(`API responded ${res.status} for ${path}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

/** Wraps a live fetch with a demo-data fallback. Never throws. */
async function withFallback<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn();
  } catch {
    return fallback;
  }
}

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

export const queryKeys = {
  queue: ["intent", "queue"] as const,
  account: (id: string) => ["intent", "account", id] as const,
  briefing: ["brain", "briefing"] as const,
  signalsHistory: (days: number) => ["signals", "history", days] as const,
  pipeline: ["analytics", "pipeline"] as const,
  signalCounts: ["analytics", "signals"] as const,
  icp: ["intent", "icp"] as const,
  planUsage: ["billing", "plan-usage"] as const,
  todayStats: ["intent", "today-stats"] as const,
};

// ---------------------------------------------------------------------------
// Action Queue
// ---------------------------------------------------------------------------

async function fetchQueue(): Promise<ActionQueueEntry[]> {
  const raw = await apiFetch<Record<string, unknown>>("/api/v1/intent/queue");
  const mapped = mapQueueResponse(raw);
  if (mapped.length === 0) throw new ApiUnavailableError("empty live queue, show demo");
  return mapped;
}

export function useActionQueue() {
  return useQuery({
    queryKey: queryKeys.queue,
    queryFn: () => withFallback(fetchQueue, demoActionQueue),
    staleTime: 30_000,
  });
}

// ---------------------------------------------------------------------------
// Account profile
// ---------------------------------------------------------------------------

interface AccountProfileResponse {
  account: Account;
  signals: Signal[];
  entry?: ActionQueueEntry;
  outreachDraft?: OutreachDraft;
}

async function fetchAccount(id: string): Promise<AccountProfileResponse> {
  const raw = await apiFetch<Record<string, unknown>>(`/api/v1/intent/account/${id}`);
  return mapAccountProfileResponse(raw);
}

function demoAccountProfile(id: string): AccountProfileResponse {
  const entry = demoActionQueue.find((e) => e.account.id === id);
  const account = entry?.account ?? demoAccounts.find((a) => a.id === id);
  const signals = entry?.signals ?? demoSignals.filter((s) => s.accountId === id);
  if (!account) {
    throw new Error(`Unknown demo account: ${id}`);
  }
  return { account, signals, entry };
}

export function useAccountProfile(id: string) {
  return useQuery({
    queryKey: queryKeys.account(id),
    // demoAccountProfile() throws for any id outside the hardcoded demo
    // fixtures (e.g. every real, live-scored account). withFallback's plain
    // `fallback: T` parameter is evaluated eagerly as an argument, so calling
    // it inline here would throw before the live request ever runs, exactly
    // like the same bug already fixed in useGenerateOutreach above.
    queryFn: async () => {
      try {
        return await fetchAccount(id);
      } catch {
        return demoAccountProfile(id);
      }
    },
    enabled: Boolean(id),
  });
}

// ---------------------------------------------------------------------------
// Outreach generation
// ---------------------------------------------------------------------------

async function generateOutreach(accountId: string): Promise<OutreachDraft> {
  const raw = await apiFetch<Record<string, unknown>>(
    `/api/v1/intent/outreach/${accountId}`,
    { method: "POST" }
  );
  const mapped = mapOutreachResponse(raw, accountId);
  if (mapped.variants.length === 0) {
    throw new ApiUnavailableError("no live drafts, show demo");
  }
  return mapped;
}

export function useGenerateOutreach() {
  const client = useQueryClient();
  return useMutation({
    // buildDemoOutreach() throws for any accountId outside the hardcoded demo
    // fixtures (e.g. every real, live-scored account). withFallback's plain
    // `fallback: T` parameter is evaluated eagerly as an argument, so calling
    // it inline here would throw before the live request ever runs. Sequence
    // the two attempts explicitly instead: try live, then the demo fixture,
    // and only fail if both are impossible (real account, backend down).
    mutationFn: async (accountId: string) => {
      try {
        return await generateOutreach(accountId);
      } catch {
        return buildDemoOutreach(accountId);
      }
    },
    onSuccess: (_data, accountId) => {
      client.invalidateQueries({ queryKey: queryKeys.account(accountId) });
    },
  });
}

// ---------------------------------------------------------------------------
// ICP profile
// ---------------------------------------------------------------------------

async function fetchICP(): Promise<ICPProfile> {
  const raw = await apiFetch<Record<string, unknown>>("/api/v1/intent/icp");
  return mapICPFromWire(raw);
}

export function useICPProfile() {
  return useQuery({
    queryKey: queryKeys.icp,
    queryFn: () => withFallback(fetchICP, demoICP),
  });
}

async function putICP(profile: ICPProfile): Promise<ICPProfile> {
  const raw = await apiFetch<Record<string, unknown>>("/api/v1/intent/icp", {
    method: "PUT",
    body: JSON.stringify(mapICPToWire(profile)),
  });
  return mapICPFromWire(raw);
}

export function useUpdateICP() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (profile: ICPProfile) => withFallback(() => putICP(profile), profile),
    onSuccess: (data) => {
      client.setQueryData(queryKeys.icp, data);
    },
  });
}

// ---------------------------------------------------------------------------
// Brain briefing + onboarding
// ---------------------------------------------------------------------------

async function fetchBriefing(): Promise<BrainBriefing> {
  const raw = await apiFetch<Record<string, unknown>>("/api/v1/brain/briefing");
  return mapBriefingResponse(raw);
}

export function useBrainBriefing() {
  return useQuery({
    queryKey: queryKeys.briefing,
    queryFn: () => withFallback(fetchBriefing, demoBriefing),
    staleTime: 60_000,
  });
}

export async function postOnboard(payload: Record<string, unknown>): Promise<{ ok: boolean }> {
  return withFallback(
    () =>
      apiFetch<{ ok: boolean }>("/api/v1/brain/onboard", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    { ok: true }
  );
}

// ---------------------------------------------------------------------------
// Signals history + stream
// ---------------------------------------------------------------------------

async function fetchSignalsHistory(days: number): Promise<Signal[]> {
  const raw = await apiFetch<Record<string, unknown>>(`/api/v1/signals/history/${days}`);
  const mapped = mapSignalsHistoryResponse(raw);
  if (mapped.length === 0) throw new ApiUnavailableError("empty live history, show demo");
  return mapped;
}

export function useSignalsHistory(days: number) {
  return useQuery({
    queryKey: queryKeys.signalsHistory(days),
    queryFn: () => withFallback(() => fetchSignalsHistory(days), demoSignals),
    staleTime: 15_000,
  });
}

/**
 * Subscribes to the live signal stream via EventSource. Falls back to a
 * demo interval emitter (cycling through bundled demo signals) if the
 * EventSource connection errors out. Returns an unsubscribe function.
 */
export function subscribeToSignalStream(
  onSignal: (signal: Signal) => void,
  onModeChange?: (mode: "live" | "demo") => void
): () => void {
  if (typeof window === "undefined") return () => {};

  let closed = false;
  let demoInterval: ReturnType<typeof setInterval> | null = null;
  let es: EventSource | null = null;

  const startDemo = () => {
    if (closed || demoInterval) return;
    onModeChange?.("demo");
    let i = 0;
    demoInterval = setInterval(() => {
      const base = demoSignals[i % demoSignals.length];
      if (base) {
        onSignal({ ...base, id: `${base.id}-demo-${Date.now()}`, detectedAt: new Date().toISOString() });
      }
      i += 1;
    }, 4500);
  };

  try {
    es = new EventSource(`${API_BASE}/api/v1/signals/stream`);
    es.onopen = () => onModeChange?.("live");
    es.onmessage = (event) => {
      try {
        onSignal(mapSignal(JSON.parse(event.data)));
      } catch {
        // ignore malformed frame
      }
    };
    es.onerror = () => {
      es?.close();
      es = null;
      startDemo();
    };
  } catch {
    startDemo();
  }

  return () => {
    closed = true;
    es?.close();
    if (demoInterval) clearInterval(demoInterval);
  };
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

async function fetchPipeline(): Promise<PipelineFunnelStage[]> {
  const raw = await apiFetch<Record<string, unknown>>("/api/v1/analytics/pipeline");
  const mapped = mapPipelineResponse(raw);
  if (mapped.length === 0) throw new ApiUnavailableError("empty live funnel, show demo");
  return mapped;
}

export function usePipelineAnalytics() {
  return useQuery({
    queryKey: queryKeys.pipeline,
    queryFn: () => withFallback(fetchPipeline, demoPipeline),
  });
}

async function fetchSignalCounts(): Promise<SignalTypeCount[]> {
  return apiFetch<SignalTypeCount[]>("/api/v1/analytics/signals");
}

export function useSignalAnalytics() {
  return useQuery({
    queryKey: queryKeys.signalCounts,
    queryFn: () => withFallback(fetchSignalCounts, demoSignalCounts),
  });
}

export function useTodayStats() {
  return useQuery({
    queryKey: queryKeys.todayStats,
    queryFn: () => withFallback(async () => demoTodayStats, demoTodayStats),
    staleTime: 30_000,
  });
}

export function usePlanUsage() {
  return useQuery({
    queryKey: queryKeys.planUsage,
    queryFn: () => withFallback(async () => demoPlanUsage, demoPlanUsage),
  });
}

// ---------------------------------------------------------------------------
// Brain chat (SSE streaming with graceful fallback)
// ---------------------------------------------------------------------------

export interface AskBrainOptions {
  question: string;
  onToken: (token: string) => void;
  onDone: () => void;
}

/**
 * Streams tokens from POST /api/v1/brain/ask. Falls back to a simulated
 * token stream built from a canned demo answer if the request fails or the
 * response body cannot be read as a stream.
 */
export async function askBrain({ question, onToken, onDone }: AskBrainOptions): Promise<void> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    const res = await fetch(`${API_BASE}/api/v1/brain/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    });
    clearTimeout(timeout);
    if (!res.ok || !res.body) throw new ApiUnavailableError("brain/ask unavailable");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    // Per the SSE spec, one logical event can span multiple consecutive
    // "data:" lines, whose values are joined by "\n"; the event ends at
    // the blank line. The backend relies on this (see brain.py's
    // encode_sse_event) to send chunks that contain embedded newlines
    // (e.g. markdown section breaks in demo-mode fallback text) without
    // corrupting them — a naive per-line parser would see the
    // continuation after an embedded newline as a line with no "data:"
    // prefix and silently drop it, eating whole words.
    let eventLines: string[] = [];
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (line.startsWith("data:")) {
          eventLines.push(line.replace(/^data: ?/, ""));
          continue;
        }
        if (line === "" && eventLines.length > 0) {
          const payload = eventLines.join("\n");
          eventLines = [];
          if (payload && payload !== "[DONE]") onToken(payload);
        }
      }
    }
    onDone();
  } catch {
    await simulateBrainStream(question, onToken, onDone);
  }
}

async function simulateBrainStream(
  question: string,
  onToken: (token: string) => void,
  onDone: () => void
): Promise<void> {
  const { demoBrainAnswer } = await import("./demo-data");
  const answer = demoBrainAnswer(question);
  const words = answer.split(" ");
  for (const word of words) {
    onToken(word + " ");
    // eslint-disable-next-line no-await-in-loop
    await new Promise((r) => setTimeout(r, 18));
  }
  onDone();
}
