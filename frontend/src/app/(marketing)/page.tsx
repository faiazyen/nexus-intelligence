import Link from "next/link";
import { PricingTable } from "@/components/marketing/PricingTable";

const SIGNAL_TYPES = [
  { icon: "◇", name: "Job postings", meaning: "Approved budget sitting next to an unsolved problem." },
  { icon: "△", name: "Leadership changes", meaning: "Every contract the predecessor signed is now under review." },
  { icon: "$", name: "Funding rounds", meaning: "A new mandate to build the growth machine now." },
  { icon: "▤", name: "Procurement notices", meaning: "The RFP exists 4 to 6 months before you usually see it." },
  { icon: "◉", name: "Earnings language", meaning: "“We're investing in X” is an active budget allocation." },
  { icon: "⌁", name: "Tech stack changes", meaning: "Switching vendors opens a review window for everything." },
  { icon: "≋", name: "News and PR", meaning: "Each announcement reshuffles priorities and vendor lists." },
  { icon: "▦", name: "SEC and 13F filings", meaning: "Capital moves 4 to 8 months before vendor spend follows." },
];

const LOOP = [
  { step: "01", name: "Monitor", body: "Continuous surveillance of 10,000+ daily triggers across public records, filings, job posts, and procurement portals." },
  { step: "02", name: "Reason", body: "Claude-powered interpretation of every signal through the lens of your specific business, offer, and past wins." },
  { step: "03", name: "Score", body: "Every account ranked by urgency, ICP fit, and budget probability. Only accounts scoring 70+ reach your queue." },
  { step: "04", name: "Act", body: "Signal-specific outreach in three frames, drafted and ready to send in one click. No blank page, ever." },
];

const COMPETITORS = [
  { name: "Bombora", weakness: "Pure data layer. No activation, no action guidance.", price: "$25K+/yr" },
  { name: "6sense", weakness: "Enterprise-only. Long onboarding, needs a full ABM team.", price: "$120K+/yr" },
  { name: "ZoomInfo Intent", weakness: "Data and contacts, but no agentic action layer.", price: "$15K+/yr" },
  { name: "Apollo / Clay", weakness: "Contact databases and enrichment. No reasoning, no intent prediction.", price: "$99+/mo" },
];

const STATS = [
  { stat: "15-25%", label: "reply rates on signal-based outreach, vs 1-5% generic" },
  { stat: "2.4x", label: "higher pipeline conversion with signal-based GTM" },
  { stat: "41%", label: "shorter sales cycles when you arrive before the RFP" },
];

export default function LandingPage() {
  return (
    <main>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-6xl px-4 pb-20 pt-24 sm:px-6">
          <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-nexus-cyan">
            Pre-RFP signal intelligence
          </p>
          <h1 className="mt-5 max-w-3xl font-display text-4xl font-semibold leading-[1.08] text-nexus-text sm:text-6xl">
            Know Who&apos;s About to Buy. Before Anyone Else Does.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-nexus-muted">
            NEXUS monitors 10,000+ daily signals and tells you which companies have
            budget, a problem, and no vendor, before they write the RFP.
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
              Open the live demo
            </Link>
          </div>
          <div className="mt-14 grid grid-cols-1 gap-6 border-t border-nexus-border pt-8 sm:grid-cols-3">
            {STATS.map((item) => (
              <div key={item.stat}>
                <p className="font-mono text-3xl font-bold tabular-nums text-nexus-cyan">{item.stat}</p>
                <p className="mt-1 text-xs leading-relaxed text-nexus-muted">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Timing asymmetry story */}
      <section className="border-y border-nexus-border bg-nexus-surface/40">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <div className="grid gap-10 lg:grid-cols-2">
            <div>
              <h2 className="font-display text-3xl font-semibold leading-tight text-nexus-text">
                By the time you see the RFP, the deal is already decided.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-nexus-muted">
                Six weeks earlier, a CMO named the problem in a meeting you were not in.
                Finance approved a budget. Procurement was told to run a comparison.
                The vendor who wins is the one who was in the room when the problem was
                first named, 4 to 8 months before the RFP exists.
              </p>
              <p className="mt-4 text-base leading-relaxed text-nexus-text">
                NEXUS makes that timing advantage a system, not luck.
              </p>
            </div>
            <div className="nexus-card p-6 font-mono text-sm">
              <p className="text-nexus-muted">{"// the invisible timeline of a deal"}</p>
              <ul className="mt-4 space-y-3">
                <li className="flex justify-between gap-4">
                  <span className="text-nexus-red">T-8 months</span>
                  <span className="text-right text-nexus-text">Problem named internally</span>
                </li>
                <li className="flex justify-between gap-4">
                  <span className="text-nexus-amber">T-6 months</span>
                  <span className="text-right text-nexus-text">Budget approved by finance</span>
                </li>
                <li className="flex justify-between gap-4">
                  <span className="text-nexus-amber">T-4 months</span>
                  <span className="text-right text-nexus-text">Advisors already in the room</span>
                </li>
                <li className="flex justify-between gap-4">
                  <span className="text-nexus-cyan">T-0</span>
                  <span className="text-right text-nexus-text">RFP published. Comparison theater begins.</span>
                </li>
                <li className="mt-2 border-t border-nexus-border pt-3 text-nexus-emerald">
                  NEXUS puts you in at T-8. Everyone else arrives at T-0.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="font-display text-3xl font-semibold text-nexus-text">
          One closed loop. Monitor. Reason. Score. Act.
        </h2>
        <p className="mt-3 max-w-2xl text-base text-nexus-muted">
          Intent tools hand you data and leave you to figure out what to do with it.
          NEXUS closes the signal-to-action gap end to end.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {LOOP.map((item) => (
            <div key={item.step} className="nexus-card p-5">
              <span className="font-mono text-xs text-nexus-cyan">{item.step}</span>
              <h3 className="mt-2 text-base font-semibold text-nexus-text">{item.name}</h3>
              <p className="mt-2 text-sm leading-relaxed text-nexus-muted">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Two products */}
      <section className="border-y border-nexus-border bg-nexus-surface/40">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="nexus-card p-6">
              <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-nexus-emerald">
                Product 1
              </p>
              <h3 className="mt-2 font-display text-2xl font-semibold text-nexus-text">NEXUS BRAIN</h3>
              <p className="mt-3 text-sm leading-relaxed text-nexus-muted">
                A living AI brain that learns your business: your ICP, your offer, your
                past wins, your competitors. It delivers daily briefings, coaches you
                through open deals, and drafts proposals grounded in what has actually
                won for you before.
              </p>
              <ul className="mt-4 space-y-1.5 text-sm text-nexus-text">
                <li>+ Daily intelligence briefing at 7am</li>
                <li>+ Deal coaching with tactical precision</li>
                <li>+ Proposal drafts built on your win patterns</li>
              </ul>
            </div>
            <div className="nexus-card p-6">
              <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-nexus-cyan">
                Product 2
              </p>
              <h3 className="mt-2 font-display text-2xl font-semibold text-nexus-text">NEXUS INTENT</h3>
              <p className="mt-3 text-sm leading-relaxed text-nexus-muted">
                A six-agent system that watches 10,000+ signals a day, scores every
                account on urgency, fit, and budget probability, and routes the hottest
                ones to your Action Queue with outreach already written.
              </p>
              <ul className="mt-4 space-y-1.5 text-sm text-nexus-text">
                <li>+ 8 signal types, refreshed continuously</li>
                <li>+ NEXUS Score with a full explanation, every account</li>
                <li>+ Three outreach frames, ready in one click</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Signal grid */}
      <section id="signals" className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="font-display text-3xl font-semibold text-nexus-text">
          Eight signals that fire months before the RFP
        </h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {SIGNAL_TYPES.map((signal) => (
            <div key={signal.name} className="nexus-card p-5">
              <span className="font-mono text-lg text-nexus-cyan">{signal.icon}</span>
              <h3 className="mt-2 text-sm font-semibold text-nexus-text">{signal.name}</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-nexus-muted">{signal.meaning}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Competitor strip */}
      <section className="border-y border-nexus-border bg-nexus-surface/40">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <h2 className="font-display text-3xl font-semibold text-nexus-text">
            They show you data. NEXUS closes the loop.
          </h2>
          <div className="mt-8 overflow-x-auto">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead>
                <tr className="border-b border-nexus-border text-xs uppercase tracking-wider text-nexus-muted">
                  <th className="py-3 pr-4 font-medium">Platform</th>
                  <th className="py-3 pr-4 font-medium">The gap</th>
                  <th className="py-3 font-medium">Price</th>
                </tr>
              </thead>
              <tbody>
                {COMPETITORS.map((competitor) => (
                  <tr key={competitor.name} className="border-b border-nexus-border/60">
                    <td className="py-3 pr-4 font-medium text-nexus-text">{competitor.name}</td>
                    <td className="py-3 pr-4 text-nexus-muted">{competitor.weakness}</td>
                    <td className="py-3 font-mono tabular-nums text-nexus-muted">{competitor.price}</td>
                  </tr>
                ))}
                <tr>
                  <td className="py-3 pr-4 font-semibold text-nexus-cyan">NEXUS</td>
                  <td className="py-3 pr-4 text-nexus-text">
                    Signals, reasoning, scoring, and ready-to-send outreach in one loop.
                  </td>
                  <td className="py-3 font-mono font-semibold tabular-nums text-nexus-cyan">$299/mo</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="font-display text-3xl font-semibold text-nexus-text">
          Enterprise intelligence. Operator pricing.
        </h2>
        <p className="mt-3 max-w-2xl text-base text-nexus-muted">
          Bombora starts at $25K a year. 6sense starts at $10K a month. NEXUS starts
          where they never bothered to look.
        </p>
        <div className="mt-8">
          <PricingTable />
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-t border-nexus-border">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
          <h2 className="mx-auto max-w-2xl font-display text-3xl font-semibold text-nexus-text sm:text-4xl">
            Your next client already has the problem. Be the first one in the room.
          </h2>
          <Link
            href="/app/onboarding"
            className="focus-ring mt-8 inline-block rounded bg-nexus-cyan px-6 py-3 text-sm font-semibold text-nexus-bg hover:bg-nexus-cyan/90"
          >
            See Your First 10 Hot Accounts Free
          </Link>
          <p className="mt-3 text-xs text-nexus-muted">No credit card. Live in under 10 minutes.</p>
        </div>
      </section>
    </main>
  );
}
