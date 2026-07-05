import type { Metadata } from "next";
import { PersonaPage, type PersonaContent } from "@/components/marketing/PersonaPage";

export const metadata: Metadata = {
  title: "NEXUS for Solo Consultants",
  description:
    "Stop waiting for referrals. NEXUS finds companies with budget and a problem before they write the RFP.",
};

const content: PersonaContent = {
  badge: "For solo consultants",
  headline: "Stop Waiting For Referrals. Start Getting in the Room Before the Meeting.",
  subhead:
    "You are one person. You cannot cold-call 500 companies and you should not have to. NEXUS watches the market for you and hands you the five accounts worth your week, with the first message already written.",
  pains: [
    {
      title: "Referrals are a ceiling",
      body: "Your pipeline is whoever happens to mention you this quarter. Great months and dead months, and no control over either.",
    },
    {
      title: "RFPs are a trap",
      body: "By the time a company invites you to bid, an insider has shaped the spec. You are column fodder for someone else's win.",
    },
    {
      title: "Prospecting eats delivery",
      body: "Every hour hunting for leads is an hour not billed. Most solos simply stop prospecting when busy, then crash when the project ends.",
    },
  ],
  playbook: [
    {
      step: "STEP 1",
      title: "Teach NEXUS your business once",
      body: "Paste your past wins, your offer, and your ideal client. Ten minutes. The Brain remembers everything.",
    },
    {
      step: "STEP 2",
      title: "Check the queue with your coffee",
      body: "Each morning, a ranked list of companies with a live trigger: new exec, fresh funding, a role they cannot fill. Only scores above 70 make the cut.",
    },
    {
      step: "STEP 3",
      title: "Send the message that lands",
      body: "Three drafts per account, each referencing the exact moment the prospect is living through. Pick one, tweak a word, send.",
    },
  ],
  proof: [
    { stat: "15-25%", label: "reply rates on signal-referenced outreach" },
    { stat: "500", label: "accounts monitored for you on the Solo plan" },
    { stat: "$299", label: "per month, vs $25K+ for enterprise intent tools" },
  ],
  closingLine: "One good client pays for NEXUS for three years. The queue is waiting.",
};

export default function SoloPage() {
  return <PersonaPage content={content} />;
}
