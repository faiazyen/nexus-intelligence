"use client";

import { useCostSummary } from "@/lib/api";

const SHORT_MODEL_NAME: Record<string, string> = {
  "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": "free tier",
  "deepseek/deepseek-v4-flash": "deepseek-flash",
  "moonshotai/kimi-k2-thinking": "kimi-k2-thinking",
  "anthropic/claude-opus-4.8": "claude-opus-4.8",
};

function shortName(model: string): string {
  return SHORT_MODEL_NAME[model] ?? model.split("/").pop() ?? model;
}

const PURPOSE_ORDER = ["classify", "outreach", "brain"];

export function CostFooter() {
  const { data } = useCostSummary();
  if (!data) return null;

  const purposeParts = PURPOSE_ORDER.filter((p) => p in data.byPurpose).map((purpose) => {
    const cost = data.byPurpose[purpose] ?? 0;
    const model = data.topModelByPurpose[purpose];
    const label = cost === 0 ? "free" : model ? shortName(model) : "";
    return `${purpose}: $${cost.toFixed(2)}${label ? ` (${label})` : ""}`;
  });

  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-nexus-border bg-nexus-surface2/60 px-4 py-2 text-[11px] text-nexus-muted">
      <span className="font-mono font-semibold text-nexus-text">
        Today: ${data.totalUsd.toFixed(2)}
      </span>
      <span className="text-nexus-border">·</span>
      <span>{purposeParts.join(" | ")}</span>
      {data.overBudget && (
        <span className="ml-auto rounded border border-nexus-amber/50 bg-nexus-amber/10 px-2 py-0.5 font-semibold text-nexus-amber">
          Over daily limit (${data.dailyLimitUsd.toFixed(2)}) — routing to free tier only
        </span>
      )}
      {!data.overBudget && data.fallbackEvents.length > 0 && (
        <span className="ml-auto rounded border border-nexus-amber/50 bg-nexus-amber/10 px-2 py-0.5 font-semibold text-nexus-amber">
          ⚠️ {data.fallbackEvents.length} Claude fallback{data.fallbackEvents.length > 1 ? "s" : ""} used
          {data.fallbackEvents[0]?.reason ? ` (${data.fallbackEvents[0].reason})` : ""}
        </span>
      )}
    </div>
  );
}
