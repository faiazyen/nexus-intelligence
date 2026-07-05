"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/app", label: "Command Center", icon: "◆" },
  { href: "/app/queue", label: "Action Queue", icon: "▲" },
  { href: "/app/brain", label: "Business Brain", icon: "◈" },
  { href: "/app/signals", label: "Signal Feed", icon: "≋" },
  { href: "/app/settings", label: "Settings", icon: "⚙" },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-nexus-border bg-nexus-surface/60 backdrop-blur md:flex">
      <div className="flex items-center gap-2 border-b border-nexus-border px-5 py-5">
        <span className="font-mono text-lg font-bold tracking-tight text-nexus-cyan">N</span>
        <span className="font-mono text-sm font-semibold tracking-widest text-nexus-text">
          NEXUS
        </span>
      </div>
      <nav className="flex-1 space-y-0.5 px-3 py-4">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/app" ? pathname === "/app" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`focus-ring flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors ${
                active
                  ? "bg-nexus-cyan/10 font-semibold text-nexus-cyan"
                  : "text-nexus-muted hover:bg-white/5 hover:text-nexus-text"
              }`}
            >
              <span className="w-4 text-center text-xs">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-nexus-border px-3 py-4">
        <Link
          href="/app/onboarding"
          className="focus-ring flex items-center gap-2.5 rounded-md px-3 py-2 text-xs text-nexus-muted hover:bg-white/5 hover:text-nexus-text"
        >
          <span className="w-4 text-center">↻</span>
          Re-run onboarding
        </Link>
        <div className="mt-3 rounded-md border border-nexus-border bg-nexus-surface2 px-3 py-2.5">
          <p className="text-[11px] font-semibold text-nexus-text">Demo Org</p>
          <p className="mt-0.5 font-mono text-[10px] text-nexus-muted">NEXUS Agency plan</p>
        </div>
      </div>
    </aside>
  );
}
