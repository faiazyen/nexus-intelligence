"use client";

import { useEffect, useMemo, useState } from "react";
import { SignalFeed } from "@/components/app/SignalFeed";
import { SignalBadge } from "@/components/app/SignalBadge";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { subscribeToSignalStream, useSignalsHistory, useActionQueue } from "@/lib/api";
import { SIGNAL_TYPE_LABELS } from "@/lib/format";
import type { Signal, SignalType, UrgencyTier } from "@/lib/types";

const ALL_TYPES = Object.keys(SIGNAL_TYPE_LABELS) as SignalType[];
const TIERS: UrgencyTier[] = ["HOT", "WARM", "COOL"];

export default function SignalsPage() {
  const history = useSignalsHistory(30);
  const queue = useActionQueue();
  const [liveSignals, setLiveSignals] = useState<Signal[]>([]);
  const [mode, setMode] = useState<"live" | "demo">("demo");
  const [typeFilter, setTypeFilter] = useState<SignalType | "all">("all");
  const [tierFilter, setTierFilter] = useState<UrgencyTier | "all">("all");

  useEffect(() => {
    const unsubscribe = subscribeToSignalStream(
      (signal) => setLiveSignals((current) => [signal, ...current].slice(0, 50)),
      setMode
    );
    return unsubscribe;
  }, []);

  const accountNameById = useMemo(() => {
    const map: Record<string, string> = {};
    for (const entry of queue.data ?? []) {
      map[entry.account.id] = entry.account.companyName;
    }
    return (accountId: string) => map[accountId] ?? "Monitored account";
  }, [queue.data]);

  const merged = useMemo(() => {
    const seen = new Set<string>();
    const combined = [...liveSignals, ...(history.data ?? [])];
    return combined.filter((signal) => {
      if (seen.has(signal.id)) return false;
      seen.add(signal.id);
      if (typeFilter !== "all" && signal.signalType !== typeFilter) return false;
      if (tierFilter !== "all" && signal.urgencyTier !== tierFilter) return false;
      return true;
    });
  }, [liveSignals, history.data, typeFilter, tierFilter]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <header className="mb-5 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h1 className="font-display text-2xl font-semibold text-nexus-text">Signal Feed</h1>
          <p className="mt-1 text-sm text-nexus-muted">
            Every trigger detected across your monitored accounts, last 30 days.
          </p>
        </div>
        <span
          className={`flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider ${
            mode === "live" ? "text-nexus-emerald" : "text-nexus-amber"
          }`}
        >
          <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
          {mode === "live" ? "live stream" : "demo stream"}
        </span>
      </header>

      {/* Filters */}
      <div className="mb-5 space-y-2">
        <div className="flex flex-wrap gap-1.5">
          <FilterChip active={typeFilter === "all"} onClick={() => setTypeFilter("all")}>
            All types
          </FilterChip>
          {ALL_TYPES.map((type) => (
            <button
              key={type}
              onClick={() => setTypeFilter(typeFilter === type ? "all" : type)}
              className={`focus-ring rounded ${typeFilter === type ? "ring-1 ring-nexus-cyan" : "opacity-70 hover:opacity-100"}`}
            >
              <SignalBadge type={type} />
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5">
          <FilterChip active={tierFilter === "all"} onClick={() => setTierFilter("all")}>
            All tiers
          </FilterChip>
          {TIERS.map((tier) => (
            <FilterChip
              key={tier}
              active={tierFilter === tier}
              onClick={() => setTierFilter(tierFilter === tier ? "all" : tier)}
            >
              {tier}
            </FilterChip>
          ))}
        </div>
      </div>

      {history.isLoading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <SignalFeed
          signals={merged}
          accountNameById={accountNameById}
          emptyLabel="No signals match these filters."
        />
      )}
    </div>
  );
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`focus-ring rounded border px-2.5 py-1 text-xs font-medium ${
        active
          ? "border-nexus-cyan/60 bg-nexus-cyan/10 text-nexus-cyan"
          : "border-nexus-border text-nexus-muted hover:text-nexus-text"
      }`}
    >
      {children}
    </button>
  );
}
