"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { NexusScoreRing } from "@/components/app/NexusScoreRing";
import { SignalBadge } from "@/components/app/SignalBadge";
import { OutreachPanel } from "@/components/app/OutreachPanel";
import { TierBadge, Pill } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { SkeletonCard, SkeletonLine } from "@/components/ui/Skeleton";
import { EmptyState, ErrorState } from "@/components/ui/States";
import { useAccountProfile, useGenerateOutreach } from "@/lib/api";
import { formatDate, formatNumber, formatRelativeTime, initialsFor } from "@/lib/format";

type Tab = "timeline" | "contacts" | "outreach";

export default function AccountProfilePage() {
  const params = useParams<{ id: string }>();
  const accountId = params.id;
  const profile = useAccountProfile(accountId);
  const generateOutreach = useGenerateOutreach();
  const [tab, setTab] = useState<Tab>("timeline");

  if (profile.isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-6">
        <SkeletonLine width="40%" />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }
  if (profile.isError || !profile.data) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6">
        <ErrorState
          message="Could not load this account."
          onRetry={() => profile.refetch()}
        />
      </div>
    );
  }

  const { account, signals, entry } = profile.data;
  const score = entry?.score.compositeNexusScore ?? 0;
  const contacts = entry?.recommendedContacts ?? [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      {/* Header */}
      <header className="nexus-card flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded bg-nexus-cyan/10 font-mono text-lg font-bold text-nexus-cyan">
          {initialsFor(account.companyName)}
        </div>
        <div className="min-w-0 flex-1">
          <h1 className="font-display text-xl font-semibold text-nexus-text">
            {account.companyName}
          </h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-nexus-muted">
            <Pill>{account.industry}</Pill>
            <Pill>{formatNumber(account.employeeCount)} employees</Pill>
            <Pill>{account.geography}</Pill>
            {account.domain && (
              <a
                className="link-underline text-nexus-cyan"
                href={`https://${account.domain}`}
                target="_blank"
                rel="noreferrer"
              >
                {account.domain}
              </a>
            )}
          </div>
          {entry && (
            <p className="mt-2 text-xs text-nexus-muted">
              {entry.signalSummary}
            </p>
          )}
        </div>
        <div className="flex shrink-0 items-center gap-4">
          <NexusScoreRing score={score} size={84} strokeWidth={6} label="NEXUS" />
        </div>
      </header>

      {entry?.score.explanation && (
        <p className="mt-3 rounded border border-nexus-border bg-nexus-surface/60 px-4 py-3 font-mono text-xs leading-relaxed text-nexus-muted">
          {entry.score.explanation}
        </p>
      )}

      {/* Tabs */}
      <nav className="mt-6 flex gap-1 border-b border-nexus-border">
        {(
          [
            ["timeline", `Timeline (${signals.length})`],
            ["contacts", `Contacts (${contacts.length})`],
            ["outreach", "Outreach"],
          ] as [Tab, string][]
        ).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`focus-ring -mb-px border-b-2 px-3 py-2 text-sm font-medium ${
              tab === key
                ? "border-nexus-cyan text-nexus-cyan"
                : "border-transparent text-nexus-muted hover:text-nexus-text"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Timeline */}
      {tab === "timeline" && (
        <div className="mt-5">
          {signals.length === 0 ? (
            <EmptyState
              title="No signals yet"
              description="NEXUS has not detected activity for this account. It stays monitored."
            />
          ) : (
            <ol className="relative space-y-5 border-l border-nexus-border pl-5">
              {signals.map((signal) => (
                <li key={signal.id} className="relative">
                  <span className="absolute -left-[26px] top-1 h-2.5 w-2.5 rounded-full border border-nexus-border bg-nexus-surface" />
                  <div className="flex flex-wrap items-center gap-2">
                    <SignalBadge type={signal.signalType} />
                    <TierBadge tier={signal.urgencyTier} />
                    <span className="font-mono text-xs text-nexus-muted">
                      {formatDate(signal.detectedAt)} · {formatRelativeTime(signal.detectedAt)}
                    </span>
                  </div>
                  <p className="mt-1.5 text-sm font-medium text-nexus-text">{signal.headline}</p>
                  {signal.summary && (
                    <p className="mt-1 text-xs leading-relaxed text-nexus-muted">{signal.summary}</p>
                  )}
                </li>
              ))}
            </ol>
          )}
        </div>
      )}

      {/* Contacts */}
      {tab === "contacts" && (
        <div className="mt-5">
          {contacts.length === 0 ? (
            <EmptyState
              title="No contacts enriched yet"
              description="Recommended decision-makers appear once the account is enriched."
            />
          ) : (
            <ul className="grid gap-3 sm:grid-cols-2">
              {contacts.map((contact) => (
                <li key={contact.id} className="nexus-card flex items-center justify-between p-4">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-nexus-text">{contact.name}</p>
                    <p className="truncate text-xs text-nexus-muted">{contact.title}</p>
                    <p className="mt-1 truncate font-mono text-xs text-nexus-muted">{contact.email}</p>
                  </div>
                  <a
                    href={contact.linkedinUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="link-underline shrink-0 text-xs text-nexus-cyan"
                  >
                    LinkedIn
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Outreach */}
      {tab === "outreach" && (
        <div className="mt-5">
          {!generateOutreach.data && !generateOutreach.isPending && (
            <EmptyState
              title="No outreach generated yet"
              description="NEXUS drafts three variants anchored to this account's strongest signal: assertive, analytical, and challenger."
              action={
                <Button onClick={() => generateOutreach.mutate(accountId)}>
                  Generate Outreach
                </Button>
              }
            />
          )}
          {(generateOutreach.data || generateOutreach.isPending) && (
            <OutreachPanel
              accountId={accountId}
              draft={generateOutreach.data}
              isLoading={generateOutreach.isPending}
              isError={generateOutreach.isError}
              onRetry={() => generateOutreach.mutate(accountId)}
            />
          )}
        </div>
      )}
    </div>
  );
}
