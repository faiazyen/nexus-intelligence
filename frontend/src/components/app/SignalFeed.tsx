"use client";

import Link from "next/link";
import type { Signal } from "@/lib/types";
import { SignalBadge } from "./SignalBadge";
import { TierBadge } from "@/components/ui/Badge";
import { formatRelativeTime } from "@/lib/format";
import { EmptyState } from "@/components/ui/States";

interface SignalFeedProps {
  signals: Signal[];
  accountNameById?: (accountId: string) => string;
  emptyLabel?: string;
  dense?: boolean;
}

export function SignalFeed({ signals, accountNameById, emptyLabel, dense = false }: SignalFeedProps) {
  if (signals.length === 0) {
    return (
      <EmptyState
        title="No signals yet"
        description={emptyLabel ?? "New signals will appear here as NEXUS detects them."}
      />
    );
  }

  return (
    <ul className="divide-y divide-nexus-border">
      {signals.map((signal) => (
        <li key={signal.id} className={dense ? "py-2.5" : "py-3.5"}>
          <div className="flex items-start gap-3">
            <TierBadge tier={signal.urgencyTier} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <SignalBadge type={signal.signalType} compact />
                {accountNameById && (
                  <Link
                    href={`/app/accounts/${signal.accountId}`}
                    className="link-underline text-xs font-semibold text-nexus-text hover:text-nexus-cyan"
                  >
                    {accountNameById(signal.accountId)}
                  </Link>
                )}
                <span className="font-mono text-[11px] text-nexus-muted">
                  {formatRelativeTime(signal.detectedAt)}
                </span>
              </div>
              <p className="mt-1 text-sm font-medium text-nexus-text">{signal.headline}</p>
              {!dense && <p className="mt-0.5 text-xs leading-relaxed text-nexus-muted">{signal.summary}</p>}
              <p className="mt-1 font-mono text-[11px] text-nexus-muted">
                source: {signal.source} · window: {signal.daysToActionWindow}d
              </p>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
