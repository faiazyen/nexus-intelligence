import type { SignalType, UrgencyTier } from "./types";

export function formatRelativeTime(isoDate: string): string {
  const date = new Date(isoDate);
  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 30) return `${diffDay}d ago`;
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export const SIGNAL_TYPE_LABELS: Record<SignalType, string> = {
  job_post: "Job Posting",
  leadership_change: "Leadership Change",
  funding: "Funding",
  procurement_notice: "Procurement Notice",
  earnings_language: "Earnings Language",
  tech_change: "Tech Stack Change",
  news: "News & PR",
  filing: "SEC / Filing",
};

export const SIGNAL_TYPE_ICONS: Record<SignalType, string> = {
  job_post: "JP",
  leadership_change: "LC",
  funding: "FN",
  procurement_notice: "PN",
  earnings_language: "EL",
  tech_change: "TC",
  news: "NW",
  filing: "SF",
};

export function urgencyTierFromScore(score: number): UrgencyTier {
  if (score >= 85) return "HOT";
  if (score >= 70) return "WARM";
  return "COOL";
}

export function scoreBandColor(score: number): "red" | "cyan" | "muted" {
  if (score >= 85) return "red";
  if (score >= 70) return "cyan";
  return "muted";
}

export function tierColorClasses(tier: UrgencyTier): {
  text: string;
  bg: string;
  border: string;
  dot: string;
} {
  switch (tier) {
    case "HOT":
      return {
        text: "text-nexus-red",
        bg: "bg-nexus-red/10",
        border: "border-nexus-red/40",
        dot: "bg-nexus-red",
      };
    case "WARM":
      return {
        text: "text-nexus-amber",
        bg: "bg-nexus-amber/10",
        border: "border-nexus-amber/40",
        dot: "bg-nexus-amber",
      };
    default:
      return {
        text: "text-nexus-muted",
        bg: "bg-nexus-muted/10",
        border: "border-nexus-muted/30",
        dot: "bg-nexus-muted",
      };
  }
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-US").format(n);
}

export function initialsFor(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}
