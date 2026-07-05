import { formatNumber } from "@/lib/format";

interface Stat {
  label: string;
  value: number;
  accent?: "cyan" | "emerald" | "amber" | "red" | "text";
}

const accentClass: Record<NonNullable<Stat["accent"]>, string> = {
  cyan: "text-nexus-cyan",
  emerald: "text-nexus-emerald",
  amber: "text-nexus-amber",
  red: "text-nexus-red",
  text: "text-nexus-text",
};

export function StatBar({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-2 divide-x divide-nexus-border sm:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.label} className="px-4 py-3 first:pl-0">
          <p className="text-[11px] uppercase tracking-wider text-nexus-muted">{stat.label}</p>
          <p className={`mt-0.5 font-mono text-2xl font-semibold tabular-nums ${accentClass[stat.accent ?? "text"]}`}>
            {formatNumber(stat.value)}
          </p>
        </div>
      ))}
    </div>
  );
}
