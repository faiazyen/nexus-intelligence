import Link from "next/link";

export interface PersonaContent {
  badge: string;
  headline: string;
  subhead: string;
  pains: { title: string; body: string }[];
  playbook: { step: string; title: string; body: string }[];
  proof: { stat: string; label: string }[];
  closingLine: string;
}

export function PersonaPage({ content }: { content: PersonaContent }) {
  return (
    <main>
      <section className="mx-auto max-w-6xl px-4 pb-16 pt-20 sm:px-6">
        <span className="rounded border border-nexus-cyan/40 bg-nexus-cyan/10 px-2 py-1 font-mono text-[11px] uppercase tracking-[0.2em] text-nexus-cyan">
          {content.badge}
        </span>
        <h1 className="mt-6 max-w-3xl font-display text-4xl font-semibold leading-[1.1] text-nexus-text sm:text-5xl">
          {content.headline}
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-nexus-muted">
          {content.subhead}
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/app/onboarding"
            className="focus-ring rounded bg-nexus-cyan px-5 py-2.5 text-sm font-semibold text-nexus-bg hover:bg-nexus-cyan/90"
          >
            See Your First 10 Hot Accounts Free
          </Link>
          <Link
            href="/app"
            className="focus-ring rounded border border-nexus-border px-5 py-2.5 text-sm font-medium text-nexus-text hover:border-nexus-cyan/50"
          >
            View the live demo
          </Link>
        </div>
      </section>

      <section className="border-y border-nexus-border bg-nexus-surface/40">
        <div className="mx-auto grid max-w-6xl gap-px overflow-hidden px-4 py-14 sm:px-6 md:grid-cols-3 md:gap-4">
          {content.pains.map((pain) => (
            <div key={pain.title} className="nexus-card p-5">
              <h3 className="text-sm font-semibold text-nexus-text">{pain.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-nexus-muted">{pain.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="font-display text-2xl font-semibold text-nexus-text sm:text-3xl">
          The NEXUS playbook
        </h2>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {content.playbook.map((item) => (
            <div key={item.step} className="nexus-card p-5">
              <span className="font-mono text-xs text-nexus-cyan">{item.step}</span>
              <h3 className="mt-2 text-sm font-semibold text-nexus-text">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-nexus-muted">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-y border-nexus-border bg-nexus-surface/40">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-4 py-12 sm:grid-cols-3 sm:px-6">
          {content.proof.map((item) => (
            <div key={item.label} className="text-center">
              <p className="font-mono text-3xl font-bold tabular-nums text-nexus-cyan">{item.stat}</p>
              <p className="mt-1 text-xs uppercase tracking-wider text-nexus-muted">{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
        <h2 className="mx-auto max-w-2xl font-display text-3xl font-semibold text-nexus-text">
          {content.closingLine}
        </h2>
        <Link
          href="/app/onboarding"
          className="focus-ring mt-8 inline-block rounded bg-nexus-cyan px-6 py-3 text-sm font-semibold text-nexus-bg hover:bg-nexus-cyan/90"
        >
          See Your First 10 Hot Accounts Free
        </Link>
      </section>
    </main>
  );
}
