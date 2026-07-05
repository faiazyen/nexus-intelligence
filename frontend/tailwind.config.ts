import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        nexus: {
          bg: "#0A0E1A",
          surface: "#111827",
          surface2: "#161F2E",
          border: "#1F2937",
          cyan: "#22D3EE",
          emerald: "#10B981",
          amber: "#F59E0B",
          red: "#EF4444",
          text: "#F9FAFB",
          muted: "#9CA3AF",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
      },
      fontFeatureSettings: {
        tabular: '"tnum" 1',
      },
      boxShadow: {
        "glow-cyan": "0 0 0 1px rgba(34,211,238,0.25), 0 0 24px rgba(34,211,238,0.15)",
        "glow-red": "0 0 0 1px rgba(239,68,68,0.3), 0 0 24px rgba(239,68,68,0.18)",
        "glow-amber": "0 0 0 1px rgba(245,158,11,0.3), 0 0 24px rgba(245,158,11,0.18)",
        "glow-emerald": "0 0 0 1px rgba(16,185,129,0.3), 0 0 24px rgba(16,185,129,0.18)",
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
      keyframes: {
        "ring-draw": {
          from: { strokeDashoffset: "var(--ring-circumference)" },
          to: { strokeDashoffset: "var(--ring-offset)" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
        "fade-up": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          from: { backgroundPosition: "-200% 0" },
          to: { backgroundPosition: "200% 0" },
        },
        marquee: {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(-50%)" },
        },
      },
      animation: {
        "ring-draw": "ring-draw 1.1s cubic-bezier(0.16,1,0.3,1) forwards",
        "pulse-dot": "pulse-dot 1.6s ease-in-out infinite",
        "fade-up": "fade-up 0.5s cubic-bezier(0.16,1,0.3,1) forwards",
        shimmer: "shimmer 1.8s linear infinite",
        marquee: "marquee 28s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
