"use client";

import { useState } from "react";
import { ActionQueueCard } from "@/components/app/ActionQueueCard";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { EmptyState, ErrorState } from "@/components/ui/States";
import { useActionQueue } from "@/lib/api";

export default function ActionQueuePage() {
  const queue = useActionQueue();
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());

  const entries = (queue.data ?? []).filter((entry) => !dismissedIds.has(entry.id));

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <header className="mb-6">
        <h1 className="font-display text-2xl font-semibold text-nexus-text">Action Queue</h1>
        <p className="mt-1 text-sm text-nexus-muted">
          Accounts scoring 70+ on urgency, fit, and budget probability. Strongest first.
          Every card has outreach one click away.
        </p>
      </header>

      {queue.isLoading && (
        <div className="space-y-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {queue.isError && <ErrorState onRetry={() => queue.refetch()} />}

      {!queue.isLoading && !queue.isError && entries.length === 0 && (
        <EmptyState
          title="Queue is clear"
          description="No accounts currently score above the 70 threshold. NEXUS keeps watching; hot accounts will appear here the moment they qualify."
        />
      )}

      <div className="space-y-4">
        {entries.map((entry) => (
          <ActionQueueCard
            key={entry.id}
            entry={entry}
            onDismiss={(id) =>
              setDismissedIds((current) => new Set(current).add(id))
            }
          />
        ))}
      </div>
    </div>
  );
}
