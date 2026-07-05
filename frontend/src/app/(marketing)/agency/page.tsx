import type { Metadata } from "next";
import { PersonaPage, type PersonaContent } from "@/components/marketing/PersonaPage";

export const metadata: Metadata = {
  title: "NEXUS for Agencies",
  description:
    "Your competitors are responding to RFPs you should have originated. NEXUS puts your agency in the deal before it becomes a comparison.",
};

const content: PersonaContent = {
  badge: "For agency owners",
  headline: "Your Competitors Are Responding to RFPs You Should Have Originated.",
  subhead:
    "The agencies that win are not better at proposals. They are earlier. NEXUS watches every account in your target market and tells your team who to call this week, why, and what to say.",
  pains: [
    {
      title: "The pitch treadmill",
      body: "Your best people burn weeks on RFP responses with a 1-in-5 hit rate, competing against firms that helped write the brief.",
    },
    {
      title: "Feast and famine",
      body: "New business depends on whoever your founders know. When delivery peaks, prospecting stops, and the pipeline gap arrives on schedule.",
    },
    {
      title: "Intent tools priced for enterprises",
      body: "Bombora and 6sense want $25K to $120K a year and a dedicated ops team. That is not an agency stack.",
    },
  ],
  playbook: [
    {
      step: "STEP 1",
      title: "Load your niches and case studies",
      body: "NEXUS BRAIN ingests your verticals, offers, and win stories. Every recommendation is grounded in what your agency actually sells.",
    },
    {
      step: "STEP 2",
      title: "Give every AE a morning queue",
      body: "Leadership changes, funding rounds, procurement notices across 2,000 accounts, scored and ranked. Three seats included.",
    },
    {
      step: "STEP 3",
      title: "Originate, don't respond",
      body: "Reach the buyer while the problem is still being named. When the RFP finally goes out, you helped shape it.",
    },
  ],
  proof: [
    { stat: "2.4x", label: "pipeline conversion lift with signal-based GTM" },
    { stat: "2,000", label: "accounts monitored on the Agency plan" },
    { stat: "41%", label: "shorter cycles when you arrive pre-RFP" },
  ],
  closingLine: "Stop renting your pipeline from procurement portals. Own the moment before the market moves.",
};

export default function AgencyPage() {
  return <PersonaPage content={content} />;
}
