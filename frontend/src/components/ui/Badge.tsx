import type { UrgencyTier } from "@/lib/types";
import { tierColorClasses } from "@/lib/format";

export function TierBadge({ tier }: { tier: UrgencyTier }) {
  const c = tierColorClasses(tier);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-[11px] font-semibold tracking-wide ${c.text} ${c.bg} ${c.border}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot} ${tier === "HOT" ? "animate-pulse-dot" : ""}`} />
      {tier}
    </span>
  );
}

export function Pill({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded border border-nexus-border bg-nexus-surface2 px-2 py-0.5 text-[11px] font-medium text-nexus-muted ${className}`}
    >
      {children}
    </span>
  );
}
