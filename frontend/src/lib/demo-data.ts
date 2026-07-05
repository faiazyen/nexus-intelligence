/**
 * Bundled demo fixtures. Every API hook in src/lib/api.ts falls back to this
 * data when the backend is unreachable, so the product fully demos standalone.
 */
import type {
  Account,
  AccountScore,
  ActionQueueEntry,
  BrainBriefing,
  Contact,
  ICPProfile,
  OutreachDraft,
  PipelineFunnelStage,
  Signal,
  SignalTypeCount,
  TodayStats,
} from "./types";

// ---------------------------------------------------------------------------
// Accounts (10, across fintech / healthtech / logistics / SaaS / manufacturing)
// ---------------------------------------------------------------------------

export const demoAccounts: Account[] = [
  {
    id: "acc_meridian",
    companyName: "Meridian Capital Partners",
    domain: "meridiancapital.com",
    industry: "Fintech",
    employeeCount: 340,
    revenueEstimate: "$60M-$90M",
    geography: "New York, NY",
    techStack: ["Salesforce", "Snowflake", "Plaid"],
    lastEnrichedAt: "2026-07-04T09:12:00Z",
  },
  {
    id: "acc_ridgeline",
    companyName: "Ridgeline Health Systems",
    domain: "ridgelinehealth.com",
    industry: "Healthtech",
    employeeCount: 890,
    revenueEstimate: "$120M-$180M",
    geography: "Denver, CO",
    techStack: ["Epic", "AWS", "Workday"],
    lastEnrichedAt: "2026-07-04T07:40:00Z",
  },
  {
    id: "acc_portway",
    companyName: "Portway Logistics",
    domain: "portwaylogistics.com",
    industry: "Logistics",
    employeeCount: 1250,
    revenueEstimate: "$200M-$300M",
    geography: "Savannah, GA",
    techStack: ["SAP", "Project44", "Oracle"],
    lastEnrichedAt: "2026-07-03T22:05:00Z",
  },
  {
    id: "acc_verdant",
    companyName: "Verdant Analytics",
    domain: "verdantanalytics.io",
    industry: "SaaS",
    employeeCount: 85,
    revenueEstimate: "$8M-$14M",
    geography: "Austin, TX",
    techStack: ["HubSpot", "Segment", "GCP"],
    lastEnrichedAt: "2026-07-04T11:30:00Z",
  },
  {
    id: "acc_ironclad_mfg",
    companyName: "Ironclad Manufacturing Co.",
    domain: "ironcladmfg.com",
    industry: "Manufacturing",
    employeeCount: 2100,
    revenueEstimate: "$400M-$600M",
    geography: "Cleveland, OH",
    techStack: ["SAP S/4HANA", "Siemens", "Azure"],
    lastEnrichedAt: "2026-07-02T14:00:00Z",
  },
  {
    id: "acc_bluepeak",
    companyName: "BluePeak Financial",
    domain: "bluepeakfinancial.com",
    industry: "Fintech",
    employeeCount: 210,
    revenueEstimate: "$30M-$50M",
    geography: "Charlotte, NC",
    techStack: ["NetSuite", "Stripe", "Looker"],
    lastEnrichedAt: "2026-07-04T06:15:00Z",
  },
  {
    id: "acc_northgate_care",
    companyName: "Northgate Care Network",
    domain: "northgatecare.com",
    industry: "Healthtech",
    employeeCount: 560,
    revenueEstimate: "$70M-$110M",
    geography: "Minneapolis, MN",
    techStack: ["Cerner", "ServiceNow", "AWS"],
    lastEnrichedAt: "2026-07-03T18:22:00Z",
  },
  {
    id: "acc_transflow",
    companyName: "Transflow Freight",
    domain: "transflowfreight.com",
    industry: "Logistics",
    employeeCount: 640,
    revenueEstimate: "$90M-$140M",
    geography: "Memphis, TN",
    techStack: ["McLeod", "Samsara", "Snowflake"],
    lastEnrichedAt: "2026-07-04T05:50:00Z",
  },
  {
    id: "acc_lumenforge",
    companyName: "LumenForge",
    domain: "lumenforge.dev",
    industry: "SaaS",
    employeeCount: 42,
    revenueEstimate: "$4M-$7M",
    geography: "Remote (US)",
    techStack: ["Vercel", "Stripe", "Retool"],
    lastEnrichedAt: "2026-07-04T12:05:00Z",
  },
  {
    id: "acc_hartwell_industrial",
    companyName: "Hartwell Industrial Group",
    domain: "hartwellindustrial.com",
    industry: "Manufacturing",
    employeeCount: 3400,
    revenueEstimate: "$800M-$1.1B",
    geography: "Pittsburgh, PA",
    techStack: ["Oracle EBS", "PTC", "IBM Cloud"],
    lastEnrichedAt: "2026-07-01T16:40:00Z",
  },
];

const accountById = (id: string): Account => {
  const found = demoAccounts.find((a) => a.id === id);
  if (!found) throw new Error(`demo account not found: ${id}`);
  return found;
};

// ---------------------------------------------------------------------------
// Signals (20+, spanning all 8 canonical types)
// ---------------------------------------------------------------------------

export const demoSignals: Signal[] = [
  {
    id: "sig_001",
    accountId: "acc_meridian",
    signalType: "leadership_change",
    source: "LinkedIn",
    headline: "Meridian Capital names new Chief Compliance Officer",
    summary:
      "Former Goldman Sachs VP joins as CCO. Every vendor the predecessor signed is now under review inside the first 90 days.",
    urgencyTier: "HOT",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T09:00:00Z",
    status: "scored",
    daysToActionWindow: 22,
  },
  {
    id: "sig_002",
    accountId: "acc_meridian",
    signalType: "job_post",
    source: "LinkedIn Jobs",
    headline: "Meridian posts \"Head of Regulatory Technology\" role",
    summary:
      "New senior role with budget authority, reporting directly to the new CCO. Team build-out signals an approved and unspent budget line.",
    urgencyTier: "HOT",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T08:10:00Z",
    status: "scored",
    daysToActionWindow: 30,
  },
  {
    id: "sig_003",
    accountId: "acc_meridian",
    signalType: "procurement_notice",
    source: "State Procurement Portal",
    headline: "Pre-solicitation notice: compliance monitoring tooling",
    summary:
      "RFI published for compliance monitoring software. Formal RFP is 4-6 months out. Vendors in the room now shape the requirements.",
    urgencyTier: "HOT",
    budgetImplication: "CONFIRMED",
    detectedAt: "2026-07-03T20:00:00Z",
    status: "scored",
    daysToActionWindow: 14,
  },
  {
    id: "sig_004",
    accountId: "acc_ridgeline",
    signalType: "funding",
    source: "Crunchbase",
    headline: "Ridgeline Health closes $45M growth round",
    summary:
      "New capital earmarked for platform modernization per the press release. CEO mandate to move fast on vendor decisions within two quarters.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T07:30:00Z",
    status: "scored",
    daysToActionWindow: 45,
  },
  {
    id: "sig_005",
    accountId: "acc_ridgeline",
    signalType: "earnings_language",
    source: "Earnings Call Transcript",
    headline: "CFO cites \"investing in patient data infrastructure\" on Q2 call",
    summary:
      "Direct budget-allocation language. Historically precedes a vendor selection process by 60-90 days.",
    urgencyTier: "WARM",
    budgetImplication: "CONFIRMED",
    detectedAt: "2026-07-03T15:00:00Z",
    status: "scored",
    daysToActionWindow: 51,
  },
  {
    id: "sig_006",
    accountId: "acc_portway",
    signalType: "tech_change",
    source: "BuiltWith",
    headline: "Portway Logistics drops legacy TMS integration layer",
    summary:
      "Job postings reference migration off a 12-year-old TMS. Switching vendors opens a full review window across the stack.",
    urgencyTier: "WARM",
    budgetImplication: "POSSIBLE",
    detectedAt: "2026-07-03T21:40:00Z",
    status: "scored",
    daysToActionWindow: 38,
  },
  {
    id: "sig_007",
    accountId: "acc_portway",
    signalType: "job_post",
    source: "Indeed",
    headline: "Portway hires \"Director of Supply Chain Digitization\"",
    summary:
      "New director-level role focused explicitly on vendor consolidation and digitization roadmap for FY27.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-02T13:20:00Z",
    status: "scored",
    daysToActionWindow: 40,
  },
  {
    id: "sig_008",
    accountId: "acc_verdant",
    signalType: "news",
    source: "TechCrunch",
    headline: "Verdant Analytics announces enterprise tier launch",
    summary:
      "Product expansion into enterprise segment reshuffles GTM priorities and opens a review of supporting vendor stack.",
    urgencyTier: "COOL",
    budgetImplication: "POSSIBLE",
    detectedAt: "2026-07-04T11:00:00Z",
    status: "scored",
    daysToActionWindow: 25,
  },
  {
    id: "sig_009",
    accountId: "acc_verdant",
    signalType: "leadership_change",
    source: "LinkedIn",
    headline: "Verdant Analytics appoints first VP of Revenue",
    summary:
      "First-ever revenue leadership hire. New exec typically re-evaluates every vendor within the first quarter.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-03T09:45:00Z",
    status: "scored",
    daysToActionWindow: 60,
  },
  {
    id: "sig_010",
    accountId: "acc_ironclad_mfg",
    signalType: "filing",
    source: "SEC EDGAR",
    headline: "Ironclad Manufacturing 8-K discloses plant automation capex",
    summary:
      "Filing discloses a nine-figure capex line for automation over the next 18 months. Capital moves 4-8 months before vendor spend follows.",
    urgencyTier: "WARM",
    budgetImplication: "CONFIRMED",
    detectedAt: "2026-07-02T12:00:00Z",
    status: "scored",
    daysToActionWindow: 70,
  },
  {
    id: "sig_011",
    accountId: "acc_ironclad_mfg",
    signalType: "procurement_notice",
    source: "SAM.gov",
    headline: "Ironclad subsidiary files pre-solicitation for MES upgrade",
    summary:
      "Manufacturing execution system upgrade pre-solicitation. RFP window projected in 4-5 months.",
    urgencyTier: "HOT",
    budgetImplication: "CONFIRMED",
    detectedAt: "2026-07-01T17:10:00Z",
    status: "scored",
    daysToActionWindow: 18,
  },
  {
    id: "sig_012",
    accountId: "acc_bluepeak",
    signalType: "job_post",
    source: "LinkedIn Jobs",
    headline: "BluePeak Financial opens \"VP of Risk Operations\"",
    summary:
      "New VP-level risk role with a mandate to modernize monitoring tooling within the first two quarters.",
    urgencyTier: "HOT",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T06:00:00Z",
    status: "scored",
    daysToActionWindow: 27,
  },
  {
    id: "sig_013",
    accountId: "acc_bluepeak",
    signalType: "funding",
    source: "Crunchbase",
    headline: "BluePeak Financial closes Series C at $85M",
    summary:
      "Fresh capital and a board mandate to scale infrastructure. New CEO mandate to build the GTM and ops machine now.",
    urgencyTier: "HOT",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-03T10:30:00Z",
    status: "scored",
    daysToActionWindow: 33,
  },
  {
    id: "sig_014",
    accountId: "acc_bluepeak",
    signalType: "earnings_language",
    source: "Investor Update Letter",
    headline: "Founder letter cites \"doubling down on compliance infrastructure\"",
    summary:
      "Direct budget-allocation language in a public investor letter, dated within the last two weeks.",
    urgencyTier: "HOT",
    budgetImplication: "CONFIRMED",
    detectedAt: "2026-07-03T09:15:00Z",
    status: "scored",
    daysToActionWindow: 40,
  },
  {
    id: "sig_015",
    accountId: "acc_northgate_care",
    signalType: "leadership_change",
    source: "PR Newswire",
    headline: "Northgate Care Network names new CIO",
    summary:
      "New CIO from a competing health system. First 90 days typically include a full vendor stack review.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-03T18:00:00Z",
    status: "scored",
    daysToActionWindow: 55,
  },
  {
    id: "sig_016",
    accountId: "acc_northgate_care",
    signalType: "tech_change",
    source: "Job Post Tech Mentions",
    headline: "Northgate lists Cerner-to-Epic migration in IT job posts",
    summary:
      "Full EHR migration underway. Every adjacent vendor relationship becomes a live conversation during this window.",
    urgencyTier: "COOL",
    budgetImplication: "POSSIBLE",
    detectedAt: "2026-07-02T08:40:00Z",
    status: "scored",
    daysToActionWindow: 80,
  },
  {
    id: "sig_017",
    accountId: "acc_transflow",
    signalType: "news",
    source: "Freight Waves",
    headline: "Transflow Freight announces Memphis hub expansion",
    summary:
      "Physical footprint expansion typically precedes an operations tooling and vendor evaluation cycle.",
    urgencyTier: "COOL",
    budgetImplication: "POSSIBLE",
    detectedAt: "2026-07-04T05:30:00Z",
    status: "scored",
    daysToActionWindow: 60,
  },
  {
    id: "sig_018",
    accountId: "acc_transflow",
    signalType: "job_post",
    source: "Indeed",
    headline: "Transflow hires \"Fleet Technology Manager\"",
    summary:
      "New role overseeing telematics and fleet software vendor relationships, reporting to COO.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-03T14:10:00Z",
    status: "scored",
    daysToActionWindow: 42,
  },
  {
    id: "sig_019",
    accountId: "acc_lumenforge",
    signalType: "funding",
    source: "Crunchbase",
    headline: "LumenForge raises $6M seed round",
    summary:
      "First institutional round. New mandate to stand up GTM function from scratch within the next two quarters.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T12:00:00Z",
    status: "scored",
    daysToActionWindow: 50,
  },
  {
    id: "sig_020",
    accountId: "acc_lumenforge",
    signalType: "leadership_change",
    source: "LinkedIn",
    headline: "LumenForge hires first Head of Sales",
    summary:
      "First revenue leader hired post-seed. Every tooling decision made pre-hire is being revisited this month.",
    urgencyTier: "HOT",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T11:50:00Z",
    status: "scored",
    daysToActionWindow: 20,
  },
  {
    id: "sig_021",
    accountId: "acc_hartwell_industrial",
    signalType: "filing",
    source: "SEC EDGAR",
    headline: "Hartwell Industrial 10-Q flags supply chain digitization initiative",
    summary:
      "Quarterly filing names supply chain digitization as a named strategic initiative for the fiscal year.",
    urgencyTier: "COOL",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-01T16:00:00Z",
    status: "scored",
    daysToActionWindow: 85,
  },
  {
    id: "sig_022",
    accountId: "acc_hartwell_industrial",
    signalType: "procurement_notice",
    source: "State Procurement Portal",
    headline: "Hartwell subsidiary posts RFI for plant floor analytics",
    summary:
      "Pre-solicitation notice for a plant floor analytics platform. Formal RFP anticipated in Q4.",
    urgencyTier: "WARM",
    budgetImplication: "CONFIRMED",
    detectedAt: "2026-06-30T22:15:00Z",
    status: "scored",
    daysToActionWindow: 95,
  },
  {
    id: "sig_023",
    accountId: "acc_ridgeline",
    signalType: "job_post",
    source: "LinkedIn Jobs",
    headline: "Ridgeline posts \"Director of Interoperability\"",
    summary:
      "New director role focused on data platform vendor selection, funded by the recent growth round.",
    urgencyTier: "WARM",
    budgetImplication: "PROBABLE",
    detectedAt: "2026-07-04T07:10:00Z",
    status: "scored",
    daysToActionWindow: 48,
  },
  {
    id: "sig_024",
    accountId: "acc_verdant",
    signalType: "tech_change",
    source: "BuiltWith",
    headline: "Verdant Analytics adds Segment CDP to stack",
    summary:
      "New data infrastructure signals an active buildout phase for GTM and analytics tooling.",
    urgencyTier: "COOL",
    budgetImplication: "POSSIBLE",
    detectedAt: "2026-07-02T10:20:00Z",
    status: "scored",
    daysToActionWindow: 55,
  },
];

const signalsForAccount = (accountId: string): Signal[] =>
  demoSignals
    .filter((s) => s.accountId === accountId)
    .sort((a, b) => new Date(b.detectedAt).getTime() - new Date(a.detectedAt).getTime());

// ---------------------------------------------------------------------------
// Scores + Action Queue
// ---------------------------------------------------------------------------

const scoreMap: Record<string, AccountScore> = {
  acc_meridian: {
    accountId: "acc_meridian",
    urgency: 92,
    fit: 88,
    budgetProbability: 95,
    compositeNexusScore: 92,
    scoredAt: "2026-07-04T09:15:00Z",
    explanation:
      "New CCO plus an open regulatory-tech req plus a live procurement pre-solicitation. Three converging signals inside a 30-day window.",
    signalIds: ["sig_001", "sig_002", "sig_003"],
  },
  acc_bluepeak: {
    accountId: "acc_bluepeak",
    urgency: 89,
    fit: 84,
    budgetProbability: 90,
    compositeNexusScore: 90,
    scoredAt: "2026-07-04T06:20:00Z",
    explanation:
      "Series C plus a new VP of Risk Operations plus explicit founder-letter budget language. Fresh capital with a named mandate.",
    signalIds: ["sig_012", "sig_013", "sig_014"],
  },
  acc_ironclad_mfg: {
    accountId: "acc_ironclad_mfg",
    urgency: 81,
    fit: 79,
    budgetProbability: 92,
    compositeNexusScore: 84,
    scoredAt: "2026-07-02T12:10:00Z",
    explanation:
      "Nine-figure capex disclosure plus a live MES pre-solicitation. Capital already committed, vendor selection window is open now.",
    signalIds: ["sig_010", "sig_011"],
  },
  acc_lumenforge: {
    accountId: "acc_lumenforge",
    urgency: 78,
    fit: 71,
    budgetProbability: 76,
    compositeNexusScore: 75,
    scoredAt: "2026-07-04T12:10:00Z",
    explanation:
      "Fresh seed round plus first sales leader hired. Every pre-hire vendor decision is under active review this month.",
    signalIds: ["sig_019", "sig_020"],
  },
  acc_ridgeline: {
    accountId: "acc_ridgeline",
    urgency: 74,
    fit: 80,
    budgetProbability: 83,
    compositeNexusScore: 75,
    scoredAt: "2026-07-04T07:45:00Z",
    explanation:
      "Growth round earmarked for platform modernization, reinforced by earnings-call budget language and a new director req.",
    signalIds: ["sig_004", "sig_005", "sig_023"],
  },
  acc_portway: {
    accountId: "acc_portway",
    urgency: 68,
    fit: 74,
    budgetProbability: 65,
    compositeNexusScore: 66,
    scoredAt: "2026-07-03T22:10:00Z",
    explanation:
      "TMS migration underway with a new digitization director. Budget confirmation still probable, not yet locked.",
    signalIds: ["sig_006", "sig_007"],
  },
  acc_northgate_care: {
    accountId: "acc_northgate_care",
    urgency: 60,
    fit: 77,
    budgetProbability: 58,
    compositeNexusScore: 58,
    scoredAt: "2026-07-03T18:30:00Z",
    explanation:
      "New CIO plus an active EHR migration. Strong fit, but budget signal is still building.",
    signalIds: ["sig_015", "sig_016"],
  },
  acc_transflow: {
    accountId: "acc_transflow",
    urgency: 55,
    fit: 69,
    budgetProbability: 54,
    compositeNexusScore: 51,
    scoredAt: "2026-07-04T05:55:00Z",
    explanation:
      "Hub expansion and a new fleet tech manager role suggest an emerging window, not yet urgent.",
    signalIds: ["sig_017", "sig_018"],
  },
  acc_hartwell_industrial: {
    accountId: "acc_hartwell_industrial",
    urgency: 52,
    fit: 72,
    budgetProbability: 64,
    compositeNexusScore: 50,
    scoredAt: "2026-07-01T16:20:00Z",
    explanation:
      "Named strategic initiative in the 10-Q with a supporting RFI. Long runway, worth tracking through Q4.",
    signalIds: ["sig_021", "sig_022"],
  },
  acc_verdant: {
    accountId: "acc_verdant",
    urgency: 46,
    fit: 66,
    budgetProbability: 45,
    compositeNexusScore: 40,
    scoredAt: "2026-07-04T11:10:00Z",
    explanation:
      "Enterprise tier launch and a first VP of Revenue are early indicators. Budget probability still low.",
    signalIds: ["sig_008", "sig_009", "sig_024"],
  },
};

const contactPool: Record<string, Contact[]> = {
  acc_meridian: [
    { id: "c1", name: "Dana Okafor", title: "Chief Compliance Officer", linkedinUrl: "https://linkedin.com/in/dana-okafor", email: "d.okafor@meridiancapital.com" },
    { id: "c2", name: "Marcus Webb", title: "Head of Regulatory Technology (open)", linkedinUrl: "https://linkedin.com/in/marcus-webb", email: "" },
  ],
  acc_bluepeak: [
    { id: "c3", name: "Priya Nair", title: "VP of Risk Operations", linkedinUrl: "https://linkedin.com/in/priya-nair", email: "priya.nair@bluepeakfinancial.com" },
    { id: "c4", name: "Elliot Cho", title: "CFO", linkedinUrl: "https://linkedin.com/in/elliot-cho", email: "elliot.cho@bluepeakfinancial.com" },
  ],
  acc_ironclad_mfg: [
    { id: "c5", name: "Renata Silva", title: "VP of Plant Operations", linkedinUrl: "https://linkedin.com/in/renata-silva", email: "r.silva@ironcladmfg.com" },
  ],
  acc_lumenforge: [
    { id: "c6", name: "Jordan Blake", title: "Head of Sales", linkedinUrl: "https://linkedin.com/in/jordan-blake", email: "jordan@lumenforge.dev" },
    { id: "c7", name: "Sam Iyer", title: "Founder & CEO", linkedinUrl: "https://linkedin.com/in/sam-iyer", email: "sam@lumenforge.dev" },
  ],
  acc_ridgeline: [
    { id: "c8", name: "Dr. Wendy Park", title: "Chief Information Officer", linkedinUrl: "https://linkedin.com/in/wendy-park", email: "w.park@ridgelinehealth.com" },
  ],
  acc_portway: [
    { id: "c9", name: "Tom Aldridge", title: "Director of Supply Chain Digitization", linkedinUrl: "https://linkedin.com/in/tom-aldridge", email: "t.aldridge@portwaylogistics.com" },
  ],
  acc_northgate_care: [
    { id: "c10", name: "Angela Brooks", title: "Chief Information Officer", linkedinUrl: "https://linkedin.com/in/angela-brooks", email: "a.brooks@northgatecare.com" },
  ],
  acc_transflow: [
    { id: "c11", name: "Miguel Torres", title: "Fleet Technology Manager", linkedinUrl: "https://linkedin.com/in/miguel-torres", email: "m.torres@transflowfreight.com" },
  ],
  acc_hartwell_industrial: [
    { id: "c12", name: "Karen Liu", title: "VP of Digital Transformation", linkedinUrl: "https://linkedin.com/in/karen-liu", email: "k.liu@hartwellindustrial.com" },
  ],
  acc_verdant: [
    { id: "c13", name: "Devon Marsh", title: "VP of Revenue", linkedinUrl: "https://linkedin.com/in/devon-marsh", email: "devon@verdantanalytics.io" },
  ],
};

export const demoActionQueue: ActionQueueEntry[] = Object.values(scoreMap)
  .sort((a, b) => b.compositeNexusScore - a.compositeNexusScore)
  .map((score, idx) => {
    const account = accountById(score.accountId);
    const signals = signalsForAccount(score.accountId);
    const statusCycle: ActionQueueEntry["status"][] = [
      "pending",
      "pending",
      "outreach_generated",
      "pending",
      "contacted",
    ];
    return {
      id: `queue_${score.accountId}`,
      account,
      score,
      signalSummary: score.explanation,
      signals,
      enteredQueueAt: signals[0]?.detectedAt ?? new Date().toISOString(),
      status: statusCycle[idx % statusCycle.length] as ActionQueueEntry["status"],
      daysInWindowEstimate: Math.min(...signals.map((s) => s.daysToActionWindow)),
      recommendedContacts: contactPool[score.accountId] ?? [],
    };
  });

// ---------------------------------------------------------------------------
// Outreach drafts
// ---------------------------------------------------------------------------

export function buildDemoOutreach(accountId: string): OutreachDraft {
  const account = accountById(accountId);
  const topSignal = signalsForAccount(accountId)[0];
  const signalRef = topSignal?.headline ?? "recent signal activity";

  const variants: OutreachDraft["variants"] = [
    {
      frame: "assertive",
      emailSubject: `${account.companyName}'s ${topSignal?.signalType.replace("_", " ") ?? "recent move"}`,
      emailBody: `I noticed ${signalRef.toLowerCase()}. Teams in this position usually lose six to eight weeks re-scoping vendor requirements from scratch. Worth a 15-minute call this week to compare notes before that window closes?`,
      linkedinMessage: `Saw the news on ${signalRef.toLowerCase()}. I work with teams navigating this exact transition, open to a quick call?`,
      callScript: `Hi, this is [name]. I'm calling because I saw ${signalRef.toLowerCase()}, and that usually means the team is about to spend a few weeks re-scoping vendor requirements. I've helped a few companies in a similar spot skip that step. Do you have 15 minutes this week to compare notes?`,
      positioningNote:
        "Signal indicates an open budget line with no locked-in vendor yet. Lead with the cost of re-scoping from scratch, not the product.",
    },
    {
      frame: "analytical",
      emailSubject: `Question on ${account.companyName}'s current roadmap`,
      emailBody: `${signalRef}. Companies at this stage typically evaluate three to five vendors over 90 days before deciding. I put together a short comparison framework based on what similar teams prioritized, happy to send it over.`,
      linkedinMessage: `Following ${account.companyName}'s recent move here. I built a short vendor comparison framework for teams in this exact spot, want it?`,
      callScript: `Hi, this is [name]. I saw ${signalRef.toLowerCase()} and wanted to share a short framework other teams used to evaluate vendors in the same window, no pitch, just the framework. Is now a bad time, or do you have a few minutes?`,
      positioningNote:
        "Use when the contact is process-driven. Offer the framework as the value exchange, not a meeting ask.",
    },
    {
      frame: "challenger",
      emailSubject: `What ${signalRef.split(" ").slice(0, 5).join(" ")} usually costs`,
      emailBody: `Most teams that just went through ${signalRef.toLowerCase()} underestimate how long the vendor evaluation actually takes, and it usually costs them a full quarter of the mandate they were just given. I can walk you through what that looked like for three comparable teams in 15 minutes.`,
      linkedinMessage: `Bet the timeline on ${signalRef.toLowerCase()} is tighter than it looks on paper. Worth comparing notes?`,
      callScript: `Hi, this is [name]. Direct question: given ${signalRef.toLowerCase()}, how much runway do you actually have before this needs to be locked in? Most teams I talk to underestimate it by a full quarter. Can I show you what that looked like for a comparable team?`,
      positioningNote:
        "Use when the account has visible time pressure. Challenge the assumed timeline directly, backed by a specific comparable.",
    },
  ];

  return {
    id: `draft_${accountId}`,
    accountId,
    signalReference: signalRef,
    variants,
    status: "draft",
    sentAt: null,
    replyReceivedAt: null,
  };
}

// ---------------------------------------------------------------------------
// Brain briefing
// ---------------------------------------------------------------------------

export const demoBriefing: BrainBriefing = {
  id: "briefing_20260705",
  orgId: "demo_org",
  briefingDate: "2026-07-05",
  pinnedAlerts: [
    "Meridian Capital Partners crossed the 90 threshold overnight. Procurement window closes in 14 days.",
    "BluePeak Financial's founder letter confirms budget language. Move this to the top of today's calls.",
  ],
  contentMarkdown: `## Today's Brief, July 5

**Three accounts moved into the red zone overnight.** Meridian Capital, BluePeak Financial, and Ironclad Manufacturing all now sit above 80 on composite score. Each has a live procurement or hiring signal with a window under 30 days.

### What changed since yesterday

- **Meridian Capital Partners (92)**: The regulatory-technology procurement notice moved from *draft* to *published* status. This account now has three concurrent signals inside a 30-day window, the strongest convergence NEXUS has flagged this month.
- **BluePeak Financial (90)**: Founder letter language confirmed budget intent, upgrading budget probability from *PROBABLE* to *CONFIRMED*. This is now a same-week call priority.
- **Ironclad Manufacturing (84)**: The MES pre-solicitation filing means procurement has already been instructed to run a comparison. Being in the room now shapes the requirements before they're locked.

### Who to call today

1. **Dana Okafor, CCO at Meridian Capital**: reference the regulatory-technology procurement notice directly. She named the problem; you're the first vendor to notice.
2. **Priya Nair, VP Risk Ops at BluePeak Financial**: reference the Series C and the founder letter language together. Budget is confirmed, timing is now.
3. **Renata Silva, VP Plant Ops at Ironclad Manufacturing**: reference the MES pre-solicitation. Position around shaping requirements, not responding to them.

### Market pattern worth noting

Healthtech accounts in your ICP are showing a consistent pattern this quarter: leadership change followed by an EHR migration signal within 60 days. Ridgeline Health and Northgate Care both fit this pattern right now. Worth building a signal-specific sequence for this combination since it's recurring across your book.

### Coaching note

Your reply rate on outreach referencing a procurement notice specifically is running well above your average this month. Lead with the procurement signal when it exists, before leadership change or funding.`,
};

// ---------------------------------------------------------------------------
// ICP profile
// ---------------------------------------------------------------------------

export const demoICP: ICPProfile = {
  targetIndustries: ["Fintech", "Healthtech", "Logistics", "SaaS", "Manufacturing"],
  companySizeMin: 50,
  companySizeMax: 5000,
  titlesTargeted: [
    "VP of Risk Operations",
    "Chief Compliance Officer",
    "Chief Information Officer",
    "VP of Revenue",
    "Director of Supply Chain",
  ],
  geographies: ["United States", "Canada"],
  techKeywords: ["Salesforce", "SAP", "Epic", "Snowflake", "NetSuite"],
  offerDescription:
    "Fractional GTM and revenue operations consulting for B2B companies navigating a leadership change, funding event, or system migration. Typical engagement is a 90-day sprint to rebuild the go-to-market motion around the new mandate.",
};

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export const demoPipeline: PipelineFunnelStage[] = [
  { stage: "signals", label: "Signals Detected", count: 4820 },
  { stage: "scored", label: "Scored", count: 1140 },
  { stage: "queued", label: "Queued (>=70)", count: 186 },
  { stage: "contacted", label: "Contacted", count: 94 },
  { stage: "replied", label: "Replied", count: 21 },
];

export const demoSignalCounts: SignalTypeCount[] = [
  { signalType: "job_post", tier: "HOT", count: 34 },
  { signalType: "job_post", tier: "WARM", count: 61 },
  { signalType: "job_post", tier: "COOL", count: 22 },
  { signalType: "leadership_change", tier: "HOT", count: 18 },
  { signalType: "leadership_change", tier: "WARM", count: 29 },
  { signalType: "leadership_change", tier: "COOL", count: 9 },
  { signalType: "funding", tier: "HOT", count: 12 },
  { signalType: "funding", tier: "WARM", count: 24 },
  { signalType: "funding", tier: "COOL", count: 7 },
  { signalType: "procurement_notice", tier: "HOT", count: 9 },
  { signalType: "procurement_notice", tier: "WARM", count: 14 },
  { signalType: "procurement_notice", tier: "COOL", count: 3 },
  { signalType: "earnings_language", tier: "HOT", count: 6 },
  { signalType: "earnings_language", tier: "WARM", count: 17 },
  { signalType: "earnings_language", tier: "COOL", count: 11 },
  { signalType: "tech_change", tier: "HOT", count: 4 },
  { signalType: "tech_change", tier: "WARM", count: 20 },
  { signalType: "tech_change", tier: "COOL", count: 26 },
  { signalType: "news", tier: "HOT", count: 2 },
  { signalType: "news", tier: "WARM", count: 15 },
  { signalType: "news", tier: "COOL", count: 33 },
  { signalType: "filing", tier: "HOT", count: 3 },
  { signalType: "filing", tier: "WARM", count: 11 },
  { signalType: "filing", tier: "COOL", count: 14 },
];

export const demoTodayStats: TodayStats = {
  newSignals: 47,
  queueDepth: 9,
  outreachSent: 6,
  repliesReceived: 2,
};

export const demoPlanUsage = {
  planName: "NEXUS Agency" as const,
  accountsMonitored: 1284,
  accountsLimit: 2000,
  actionQueueCreditsUsed: 0,
  actionQueueCreditsLimit: null,
  seatsUsed: 2,
  seatsLimit: 3,
  renewsOn: "2026-08-01",
};

export const demoChatQuickPrompts: string[] = [
  "Who should I call today?",
  "Coach me on the Meridian Capital deal",
  "What changed in my pipeline overnight?",
  "Draft a follow-up for BluePeak Financial",
];

export function demoBrainAnswer(question: string): string {
  const q = question.toLowerCase();
  if (q.includes("who should i call")) {
    return `Based on this morning's scoring run, call these three first:

1. **Dana Okafor at Meridian Capital Partners** (score 92). The regulatory-technology procurement notice just went live. She named the problem, you're early.
2. **Priya Nair at BluePeak Financial** (score 90). Budget language just moved from probable to confirmed in the founder letter.
3. **Renata Silva at Ironclad Manufacturing** (score 84). The MES pre-solicitation filing means procurement is already building the comparison list.

Lead every one of these with the specific signal, not your offer.`;
  }
  if (q.includes("meridian")) {
    return `**Meridian Capital Partners, deal coaching**

Three converging signals: new CCO (day 1 to 90), an open Head of Regulatory Technology req, and a live procurement pre-solicitation. This is the strongest convergence in your queue right now.

Recommended move: reference the procurement notice directly in your first line. She named the problem, and the RFP window closes in roughly 14 days on the pre-solicitation clock. Position yourself as the person shaping the requirements, not responding to them.

Avoid leading with your service description. Lead with what the notice says and what it will cost her team to scope it alone.`;
  }
  if (q.includes("changed") || q.includes("overnight")) {
    return `Overnight, three accounts crossed into red-zone territory: Meridian Capital (92), BluePeak Financial (90), and Ironclad Manufacturing (84). BluePeak's founder letter upgraded budget probability from probable to confirmed. Full detail is in today's brief on the left panel.`;
  }
  if (q.includes("bluepeak") || q.includes("follow")) {
    return `**Follow-up draft for BluePeak Financial**

Subject: BluePeak's Series C and the risk ops build-out

Priya, the founder letter mentioned doubling down on compliance infrastructure right after the Series C closed. Teams in this spot usually spend six weeks re-scoping vendor requirements before realizing the budget window is shorter than it looks. Worth 15 minutes this week to compare notes before your board check-in?

Keep the ask small. Do not mention your service by name in this first message.`;
  }
  return `Here's what I can tell you from your current business context and this week's signals: your strongest opportunities right now are concentrated in fintech accounts going through a leadership change paired with a procurement signal. That combination is converting at roughly twice the rate of any other pattern in your book this quarter. Want me to pull the specific accounts?`;
}
