"use client";

import { useState } from "react";
import type { OutreachDraft, OutreachFrame } from "@/lib/types";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/States";

interface OutreachPanelProps {
  accountId: string;
  draft?: OutreachDraft;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
}

const FRAME_LABEL: Record<OutreachFrame, string> = {
  assertive: "Assertive",
  analytical: "Analytical",
  challenger: "Challenger",
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1600);
      }}
      className="focus-ring shrink-0 rounded border border-nexus-border px-2 py-1 text-[11px] font-medium text-nexus-muted hover:border-nexus-cyan/50 hover:text-nexus-cyan"
    >
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

export function OutreachPanel({ draft, isLoading, isError, onRetry }: OutreachPanelProps) {
  const [activeFrame, setActiveFrame] = useState<OutreachFrame>("assertive");

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="flex gap-2">
          <Skeleton className="h-7 w-24" />
          <Skeleton className="h-7 w-24" />
          <Skeleton className="h-7 w-24" />
        </div>
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  if (isError || !draft) {
    return <ErrorState message="Couldn't generate outreach right now." onRetry={onRetry} />;
  }

  const variant = draft.variants.find((v) => v.frame === activeFrame) ?? draft.variants[0];
  if (!variant) return null;

  return (
    <div>
      <div className="flex gap-1 border-b border-nexus-border">
        {draft.variants.map((v) => (
          <button
            key={v.frame}
            onClick={() => setActiveFrame(v.frame)}
            className={`focus-ring border-b-2 px-3 py-2 text-xs font-semibold transition-colors ${
              activeFrame === v.frame
                ? "border-nexus-cyan text-nexus-cyan"
                : "border-transparent text-nexus-muted hover:text-nexus-text"
            }`}
          >
            {FRAME_LABEL[v.frame]}
          </button>
        ))}
      </div>

      <div className="mt-3 space-y-4">
        <div>
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-nexus-muted">
              Email
            </span>
            <CopyButton text={`Subject: ${variant.emailSubject}\n\n${variant.emailBody}`} />
          </div>
          <div className="nexus-card space-y-1.5 p-3">
            <p className="text-sm font-semibold text-nexus-text">{variant.emailSubject}</p>
            <p className="text-sm leading-relaxed text-nexus-muted">{variant.emailBody}</p>
          </div>
        </div>

        <div>
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-nexus-muted">
              LinkedIn message
            </span>
            <CopyButton text={variant.linkedinMessage} />
          </div>
          <div className="nexus-card p-3">
            <p className="text-sm leading-relaxed text-nexus-text">{variant.linkedinMessage}</p>
          </div>
        </div>

        <div>
          <div className="mb-1 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-nexus-muted">
              Call opener (30 sec)
            </span>
            <CopyButton text={variant.callScript} />
          </div>
          <div className="nexus-card p-3">
            <p className="text-sm leading-relaxed text-nexus-text">{variant.callScript}</p>
          </div>
        </div>

        <div className="rounded-md border border-nexus-cyan/25 bg-nexus-cyan/5 p-3">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-nexus-cyan">
            Positioning note
          </p>
          <p className="mt-1 text-xs leading-relaxed text-nexus-muted">{variant.positioningNote}</p>
        </div>
      </div>
    </div>
  );
}
