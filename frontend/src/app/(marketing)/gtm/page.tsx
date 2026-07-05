import type { Metadata } from "next";
import { PersonaPage, type PersonaContent } from "@/components/marketing/PersonaPage";

export const metadata: Metadata = {
  title: "NEXUS for GTM Leaders",
  description:
    "Your SDRs are prospecting into yesterday's intent data. NEXUS tells them who is buying today.",
};

const content: PersonaContent = {
  badge: "For VP Sales / GTM leaders",
  headline: "Your SDRs Are Prospecting Into Yesterday's Intent Data. NEXUS Tells Them Who's Buying Today.",
  subhead:
    "91% of B2B teams buy intent data. 24% see ROI. The gap is not the data, it is the missing action layer. NEXUS turns raw signals into scored accounts with outreach your reps can send before standup.",
  pains: [
    {
      title: "The signal-to-action gap",
      body: "Your intent platform lights up an account. Then a rep spends 40 minutes researching it, writes a generic email, and the moment passes.",
    },
    {
      title: "Activity theater",
      body: "Sequences hit quota dashboards, not buyers. 1-5% reply rates mean your team burns its TAM to hit activity numbers.",
    },
    {
      title: "Tools that don't talk",
      body: "Intent in one tab, contacts in another, messaging in a doc. Nobody closes the loop, so nobody owns the outcome.",
    },
  ],
  playbook: [
    {
      step: "STEP 1",
      title: "Point NEXUS at your ICP",
      body: "Industries, size bands, geos, tech stack, titles. Multi-ICP support on Enterprise for every segment you run.",
    },
    {
      step: "STEP 2",
      title: "Route only 70+ scores to reps",
      body: "Urgency, fit, and budget probability in one composite score with a full explanation. No more guessing which alert matters.",
    },
    {
      step: "STEP 3",
      title: "Measure the loop, not the noise",
      body: "Pipeline analytics track every signal from detection to reply, and the Memory Manager learns which signals convert for your motion.",
    },
  ],
  proof: [
    { stat: "76%", label: "of B2B orgs deploying agentic AI in GTM" },
    { stat: "10,000+", label: "accounts monitored on Enterprise" },
    { stat: "15-25%", label: "reply rates your reps can actually hit" },
  ],
  closingLine: "Give your team tomorrow's pipeline instead of last quarter's intent report.",
};

export default function GtmPage() {
  return <PersonaPage content={content} />;
}
