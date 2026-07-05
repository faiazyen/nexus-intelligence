import type { SignalType } from "@/lib/types";
import { SIGNAL_TYPE_ICONS, SIGNAL_TYPE_LABELS } from "@/lib/format";

export function SignalBadge({ type, compact = false }: { type: SignalType; compact?: boolean }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded border border-nexus-border bg-nexus-surface2 px-2 py-0.5 text-[11px] font-medium text-nexus-muted">
      <span className="font-mono text-[10px] font-bold text-nexus-cyan">
        {SIGNAL_TYPE_ICONS[type]}
      </span>
      {!compact && SIGNAL_TYPE_LABELS[type]}
    </span>
  );
}
