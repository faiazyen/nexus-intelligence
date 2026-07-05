import Link from "next/link";

interface Tier {
  name: string;
  price: string;
  period: string;
  target: string;
  features: string[];
  highlighted?: boolean;
  cta: string;
}

const tiers: Tier[] = [
  {
    name: "NEXUS Solo",
    price: "$299",
    period: "/month",
    target: "Freelance consultants and solo B2B operators",
    features: [
      "500 accounts monitored",
      "50 Action Queue credits per month",
      "NEXUS BRAIN basic",
      "All 8 signal types",
      "Signal-specific outreach drafts",
    ],
    cta: "Start free",
  },
  {
    name: "NEXUS Agency",
    price: "$799",
    period: "/month",
    target: "Agencies and boutique consultancies, 2 to 20 staff",
    features: [
      "2,000 accounts monitored",
      "Unlimited Action Queue",
      "NEXUS BRAIN full: coaching, briefings, proposals",
      "3 team seats",
      "Priority signal refresh",
    ],
    highlighted: true,
    cta: "Start free",
  },
  {
    name: "NEXUS Enterprise",
    price: "$2,499",
    period: "/month",
    target: "Mid-market consulting firms and B2B SaaS GTM teams",
    features: [
      "10,000+ accounts monitored",
      "Multi-ICP support",
      "API access and CRM integration",
      "Dedicated customer success",
      "Custom scoring calibration",
    ],
    cta: "Talk to us",
  },
  {
    name: "NEXUS AI Install",
    price: "Custom",
    period: "",
    target: "White-glove consulting install for your whole firm",
    features: [
      "Custom signal types built for you",
      "Team training and playbooks",
      "SLA and dedicated support",
      "Private deployment options",
    ],
    cta: "Contact sales",
  },
];

export function PricingTable() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {tiers.map((tier) => (
        <div
          key={tier.name}
          className={`nexus-card flex flex-col p-5 ${
            tier.highlighted ? "border-nexus-cyan/60 shadow-[0_0_24px_rgba(34,211,238,0.12)]" : ""
          }`}
        >
          {tier.highlighted && (
            <span className="mb-2 w-fit rounded bg-nexus-cyan/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-nexus-cyan">
              Most popular
            </span>
          )}
          <h3 className="text-sm font-semibold text-nexus-text">{tier.name}</h3>
          <p className="mt-2">
            <span className="font-mono text-3xl font-bold tabular-nums text-nexus-text">
              {tier.price}
            </span>
            <span className="text-sm text-nexus-muted">{tier.period}</span>
          </p>
          <p className="mt-1 text-xs text-nexus-muted">{tier.target}</p>
          <ul className="mt-4 flex-1 space-y-2">
            {tier.features.map((feature) => (
              <li key={feature} className="flex gap-2 text-xs text-nexus-text">
                <span className="text-nexus-emerald">+</span>
                {feature}
              </li>
            ))}
          </ul>
          <Link
            href="/app/onboarding"
            className={`focus-ring mt-5 rounded px-3 py-2 text-center text-sm font-semibold ${
              tier.highlighted
                ? "bg-nexus-cyan text-nexus-bg hover:bg-nexus-cyan/90"
                : "border border-nexus-border text-nexus-text hover:border-nexus-cyan/50"
            }`}
          >
            {tier.cta}
          </Link>
        </div>
      ))}
    </div>
  );
}
