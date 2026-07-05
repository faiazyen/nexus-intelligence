"use client";

import { BrainChat } from "@/components/app/BrainChat";
import { SkeletonLine } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/States";
import { useBrainBriefing } from "@/lib/api";
import { demoChatQuickPrompts } from "@/lib/demo-data";
import { formatDate } from "@/lib/format";

/** Minimal markdown rendering: headings, bold, bullets. Keeps deps at zero. */
function MarkdownLite({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="space-y-2 text-sm leading-relaxed text-nexus-text">
      {lines.map((line, index) => {
        const key = `${index}-${line.slice(0, 12)}`;
        if (line.startsWith("# ")) {
          return (
            <h2 key={key} className="pt-1 font-display text-lg font-semibold">
              {line.slice(2)}
            </h2>
          );
        }
        if (line.startsWith("## ")) {
          return (
            <h3 key={key} className="pt-2 text-xs font-semibold uppercase tracking-wider text-nexus-cyan">
              {line.slice(3)}
            </h3>
          );
        }
        if (line.startsWith("- ") || /^\d+\.\s/.test(line)) {
          return (
            <p key={key} className="flex gap-2 text-nexus-muted">
              <span className="text-nexus-cyan">›</span>
              <span dangerouslySetInnerHTML={{ __html: emphasize(line.replace(/^(-|\d+\.)\s/, "")) }} />
            </p>
          );
        }
        if (!line.trim()) return null;
        return <p key={key} className="text-nexus-muted" dangerouslySetInnerHTML={{ __html: emphasize(line) }} />;
      })}
    </div>
  );
}

function emphasize(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-nexus-text">$1</strong>');
}

export default function BrainPage() {
  const briefing = useBrainBriefing();

  return (
    <div className="grid min-h-screen lg:grid-cols-[2fr_3fr]">
      {/* Left: daily brief */}
      <section className="border-b border-nexus-border p-5 lg:border-b-0 lg:border-r">
        <div className="mb-4 flex items-baseline justify-between">
          <h1 className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">
            Today&apos;s brief
          </h1>
          {briefing.data && (
            <span className="font-mono text-xs text-nexus-muted">
              {formatDate(briefing.data.briefingDate)}
            </span>
          )}
        </div>

        {briefing.isLoading && (
          <div className="space-y-3">
            <SkeletonLine width="60%" />
            <SkeletonLine />
            <SkeletonLine />
            <SkeletonLine width="80%" />
          </div>
        )}
        {briefing.isError && <ErrorState onRetry={() => briefing.refetch()} />}
        {briefing.data && (
          <>
            {briefing.data.pinnedAlerts.length > 0 && (
              <div className="mb-4 space-y-2">
                {briefing.data.pinnedAlerts.map((alert) => (
                  <div
                    key={alert}
                    className="rounded border border-nexus-amber/40 bg-nexus-amber/10 px-3 py-2 text-xs text-nexus-amber"
                  >
                    ⚑ {alert}
                  </div>
                ))}
              </div>
            )}
            <MarkdownLite content={briefing.data.contentMarkdown} />
          </>
        )}
      </section>

      {/* Right: chat */}
      <section className="flex h-[calc(100vh-0px)] flex-col p-5">
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-nexus-muted">
          Ask the Brain
        </h2>
        <div className="nexus-card flex min-h-0 flex-1 flex-col overflow-hidden">
          <BrainChat
            quickPrompts={demoChatQuickPrompts}
            initialGreeting="I'm loaded with your business context and today's signals. Ask me who to call, how to open, or what changed in your market."
          />
        </div>
      </section>
    </div>
  );
}
