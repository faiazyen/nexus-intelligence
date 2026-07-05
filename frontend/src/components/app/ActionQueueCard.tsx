"use client";

import { useState } from "react";
import Link from "next/link";
import type { ActionQueueEntry } from "@/lib/types";
import { NexusScoreRing } from "./NexusScoreRing";
import { SignalBadge } from "./SignalBadge";
import { TierBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { OutreachPanel } from "./OutreachPanel";
import { useGenerateOutreach } from "@/lib/api";
import { formatRelativeTime } from "@/lib/format";

interface ActionQueueCardProps {
  entry: ActionQueueEntry;
  onDismiss?: (id: string) => void;
}

export function ActionQueueCard({ entry, onDismiss }: ActionQueueCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [showOutreach, setShowOutreach] = useState(false);
  const generateOutreach = useGenerateOutreach();
  const topSignal = entry.signals[0];

  const handleGenerate = () => {
    setShowOutreach(true);
    generateOutreach.mutate(entry.account.id);
  };

  return (
    <div className="nexus-card overflow-hidden">
      <div className="flex flex-col gap-4 p-4 sm:flex-row sm:items-start">
        <NexusScoreRing score={entry.score.compositeNexusScore} size={72} strokeWidth={5} />

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href={`/app/accounts/${entry.account.id}`}
              className="link-underline text-base font-semibold text-nexus-text hover:text-nexus-cyan"
            >
              {entry.account.companyName}
            </Link>
            <TierBadge tier={topSignal?.urgencyTier ?? "COOL"} />
            <span className="text-xs text-nexus-muted">
              {entry.account.industry} · {entry.account.geography}
            </span>
          </div>

          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {Array.from(new Set(entry.signals.map((s) => s.signalType))).map((t) => (
              <SignalBadge key={t} type={t} />
            ))}
          </div>

          <p className="mt-2 text-sm leading-relaxed text-nexus-muted">{entry.signalSummary}</p>

          <div className="mt-3 flex flex-wrap items-center gap-4 text-xs">
            <span className="font-mono text-nexus-amber">
              {entry.daysInWindowEstimate}d left in window
            </span>
            <span className="text-nexus-muted">
              entered queue {formatRelativeTime(entry.enteredQueueAt)}
            </span>
            <button
              onClick={() => setExpanded((v) => !v)}
              className="focus-ring link-underline font-medium text-nexus-cyan"
            >
              {expanded ? "Hide detail" : "View signals & contacts"}
            </button>
          </div>
        </div>

        <div className="flex shrink-0 gap-2 sm:flex-col">
          <Button size="sm" onClick={handleGenerate} className="w-full">
            Generate Outreach
          </Button>
          <Button size="sm" variant="secondary" onClick={() => onDismiss?.(entry.id)} className="w-full">
            Dismiss
          </Button>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-nexus-border bg-nexus-bg/40 px-4 py-4">
          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-nexus-muted">
                Full signal list
              </h4>
              <ul className="space-y-2">
                {entry.signals.map((s) => (
                  <li key={s.id} className="text-xs">
                    <div className="flex items-center gap-2">
                      <SignalBadge type={s.signalType} compact />
                      <span className="font-mono text-nexus-muted">
                        {formatRelativeTime(s.detectedAt)}
                      </span>
                    </div>
                    <p className="mt-0.5 text-nexus-text">{s.headline}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-nexus-muted">
                Recommended contacts
              </h4>
              {entry.recommendedContacts.length === 0 ? (
                <p className="text-xs text-nexus-muted">No contacts enriched yet.</p>
              ) : (
                <ul className="space-y-2">
                  {entry.recommendedContacts.map((c) => (
                    <li key={c.id} className="flex items-center justify-between text-xs">
                      <div>
                        <p className="font-medium text-nexus-text">{c.name}</p>
                        <p className="text-nexus-muted">{c.title}</p>
                      </div>
                      <a
                        href={c.linkedinUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="link-underline text-nexus-cyan"
                      >
                        LinkedIn
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

      {showOutreach && (
        <div className="border-t border-nexus-border p-4">
          <OutreachPanel
            accountId={entry.account.id}
            draft={generateOutreach.data}
            isLoading={generateOutreach.isPending}
            isError={generateOutreach.isError}
            onRetry={handleGenerate}
          />
        </div>
      )}
    </div>
  );
}
