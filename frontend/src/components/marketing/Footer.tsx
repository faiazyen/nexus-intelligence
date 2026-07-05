import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-nexus-border">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4">
        <div>
          <p className="font-mono text-base font-bold text-nexus-cyan">NEXUS</p>
          <p className="mt-2 max-w-[28ch] text-sm text-nexus-muted">
            Know who&apos;s about to buy. Before anyone else does.
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">Product</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link className="link-underline text-nexus-text" href="/#how-it-works">How it works</Link></li>
            <li><Link className="link-underline text-nexus-text" href="/#signals">Signal coverage</Link></li>
            <li><Link className="link-underline text-nexus-text" href="/#pricing">Pricing</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">Who it&apos;s for</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link className="link-underline text-nexus-text" href="/solo">Solo consultants</Link></li>
            <li><Link className="link-underline text-nexus-text" href="/agency">Agency owners</Link></li>
            <li><Link className="link-underline text-nexus-text" href="/gtm">GTM leaders</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">Platform</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link className="link-underline text-nexus-text" href="/app">Command Center</Link></li>
            <li><Link className="link-underline text-nexus-text" href="/app/onboarding">Get started</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-nexus-border py-4 text-center text-xs text-nexus-muted">
        NEXUS Intelligence. The room before the meeting.
      </div>
    </footer>
  );
}
