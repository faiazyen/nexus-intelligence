"use client";

import { useEffect, useState } from "react";
import { scoreBandColor } from "@/lib/format";

interface NexusScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  animate?: boolean;
}

const COLOR_HEX: Record<"red" | "cyan" | "muted", string> = {
  red: "#EF4444",
  cyan: "#22D3EE",
  muted: "#9CA3AF",
};

export function NexusScoreRing({
  score,
  size = 64,
  strokeWidth = 5,
  label,
  animate = true,
}: NexusScoreRingProps) {
  const [mounted, setMounted] = useState(!animate);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  const band = scoreBandColor(score);
  const color = COLOR_HEX[band];

  useEffect(() => {
    if (!animate) return;
    const raf = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(raf);
  }, [animate]);

  return (
    <div
      className="relative inline-flex shrink-0 items-center justify-center"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`NEXUS Score ${score} of 100${label ? `, ${label}` : ""}`}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1F2937"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={mounted ? offset : circumference}
          style={{
            transition: animate ? "stroke-dashoffset 1.1s cubic-bezier(0.16,1,0.3,1)" : undefined,
            filter: band === "red" ? `drop-shadow(0 0 4px ${color}80)` : undefined,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="font-mono tabular-nums font-semibold leading-none"
          style={{ fontSize: size * 0.28, color }}
        >
          {clamped}
        </span>
      </div>
    </div>
  );
}
