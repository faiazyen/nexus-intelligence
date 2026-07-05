"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/solo", label: "For Consultants" },
  { href: "/agency", label: "For Agencies" },
  { href: "/gtm", label: "For GTM Teams" },
];

export function MarketingNav() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-40 border-b border-nexus-border bg-nexus-bg/85 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="focus-ring flex items-center gap-2">
          <span className="font-mono text-lg font-bold tracking-tight text-nexus-cyan">
            NEXUS
          </span>
          <span className="hidden text-[11px] font-medium uppercase tracking-[0.2em] text-nexus-muted sm:inline">
            Intelligence
          </span>
        </Link>
        <nav className="hidden items-center gap-6 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`focus-ring text-sm ${
                pathname === link.href
                  ? "text-nexus-cyan"
                  : "text-nexus-muted hover:text-nexus-text"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Link
            href="/app"
            className="focus-ring text-sm text-nexus-muted hover:text-nexus-text"
          >
            Sign in
          </Link>
          <Link
            href="/app/onboarding"
            className="focus-ring rounded bg-nexus-cyan px-3 py-1.5 text-sm font-semibold text-nexus-bg hover:bg-nexus-cyan/90"
          >
            Start free
          </Link>
        </div>
      </div>
    </header>
  );
}
