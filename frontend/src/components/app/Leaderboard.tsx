"use client";

import Link from "next/link";
import type { ActionQueueEntry } from "@/lib/types";
import { NexusScoreRing } from "./NexusScoreRing";
import { EmptyState } from "@/components/ui/States";

export function Leaderboard({ entries }: { entries: ActionQueueEntry[] }) {
  const top10 = entries.slice(0, 10);

  if (top10.length === 0) {
    return <EmptyState title="No accounts scored yet" description="Your leaderboard fills in as accounts clear the scoring threshold." />;
  }

  return (
    <ol className="space-y-1">
      {top10.map((entry, idx) => (
        <li key={entry.id}>
          <Link
            href={`/app/accounts/${entry.account.id}`}
            className="focus-ring group flex items-center gap-3 rounded-md px-2 py-2 transition-colors hover:bg-white/5"
          >
            <span className="w-4 shrink-0 font-mono text-xs text-nexus-muted">{idx + 1}</span>
            <NexusScoreRing score={entry.score.compositeNexusScore} size={36} strokeWidth={3.5} animate={false} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-nexus-text group-hover:text-nexus-cyan">
                {entry.account.companyName}
              </p>
              <p className="truncate text-xs text-nexus-muted">{entry.account.industry}</p>
            </div>
          </Link>
        </li>
      ))}
    </ol>
  );
}
