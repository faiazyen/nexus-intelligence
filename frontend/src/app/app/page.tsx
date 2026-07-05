"use client";

import { useEffect, useMemo, useState } from "react";
import { StatBar } from "@/components/app/StatBar";
import { Leaderboard } from "@/components/app/Leaderboard";
import { SignalFeed } from "@/components/app/SignalFeed";
import { BrainChat } from "@/components/app/BrainChat";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { useActionQueue, useTodayStats, subscribeToSignalStream } from "@/lib/api";
import { demoChatQuickPrompts, demoSignals } from "@/lib/demo-data";
import type { Signal } from "@/lib/types";

const MAX_FEED_LENGTH = 30;

export default function CommandCenterPage() {
  const queue = useActionQueue();
  const stats = useTodayStats();
  const [liveSignals, setLiveSignals] = useState<Signal[]>(() => demoSignals.slice(0, 8));
  const [mode, setMode] = useState<"live" | "demo">("demo");

  useEffect(() => {
    const unsubscribe = subscribeToSignalStream(
      (signal) =>
        setLiveSignals((current) => [signal, ...current].slice(0, MAX_FEED_LENGTH)),
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

  return (
    <div className="flex min-h-screen flex-col">
      <div className="border-b border-nexus-border">
        <StatBar
          stats={[
            { label: "New signals today", value: stats.data?.newSignals ?? 0, accent: "cyan" },
            { label: "Queue depth", value: stats.data?.queueDepth ?? 0, accent: "amber" },
            { label: "Outreach sent", value: stats.data?.outreachSent ?? 0, accent: "emerald" },
            { label: "Replies received", value: stats.data?.repliesReceived ?? 0, accent: "text" },
          ]}
        />
      </div>

      <div className="grid flex-1 gap-4 p-4 lg:grid-cols-[minmax(280px,1fr)_minmax(320px,1.2fr)_minmax(300px,1fr)]">
        {/* Left: leaderboard */}
        <section className="min-w-0">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">
              NEXUS Score leaderboard
            </h2>
          </div>
          {queue.isLoading ? (
            <div className="space-y-3">
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : (
            <Leaderboard entries={(queue.data ?? []).slice(0, 10)} />
          )}
        </section>

        {/* Center: live signal feed */}
        <section className="min-w-0">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">
              Signal feed
            </h2>
            <span
              className={`flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider ${
                mode === "live" ? "text-nexus-emerald" : "text-nexus-amber"
              }`}
            >
              <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
              {mode === "live" ? "live" : "demo stream"}
            </span>
          </div>
          <SignalFeed
            signals={liveSignals}
            accountNameById={accountNameById}
            emptyLabel="Waiting for the first signal of the day."
          />
        </section>

        {/* Right: brain dock */}
        <section className="min-w-0">
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-nexus-muted">
            Business Brain
          </h2>
          <div className="nexus-card flex h-[calc(100vh-160px)] min-h-[420px] flex-col overflow-hidden">
            <BrainChat
              compact
              quickPrompts={demoChatQuickPrompts}
              initialGreeting="Morning. Two accounts crossed the 70 threshold overnight. Ask me who to call first, or open the Action Queue."
            />
          </div>
        </section>
      </div>
    </div>
  );
}
