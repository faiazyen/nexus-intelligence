"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { SignalBadge } from "@/components/app/SignalBadge";
import { useOnboardingStore } from "@/lib/onboarding-store";
import { postOnboard } from "@/lib/api";
import { SIGNAL_TYPE_LABELS } from "@/lib/format";
import type { SignalType } from "@/lib/types";

const STEPS = [
  "Company",
  "Your offer",
  "Your ICP",
  "Past wins",
  "Signals",
  "Review",
];

const INDUSTRY_OPTIONS = [
  "SaaS", "Fintech", "Healthtech", "Logistics", "Manufacturing",
  "Hospitality", "Education", "Energy", "Legal services", "E-commerce",
];
const TITLE_OPTIONS = [
  "CEO", "COO", "CIO", "CMO", "VP Sales", "VP Operations",
  "Head of Procurement", "Head of IT",
];
const GEO_OPTIONS = [
  "United States", "Canada", "United Kingdom", "Germany", "France", "Netherlands",
];
const ALL_SIGNAL_TYPES = Object.keys(SIGNAL_TYPE_LABELS) as SignalType[];

export default function OnboardingPage() {
  const router = useRouter();
  const store = useOnboardingStore();
  const [launching, setLaunching] = useState(false);

  const handleLaunch = async () => {
    setLaunching(true);
    await postOnboard({
      company: {
        name: store.companyName,
        website: store.companyWebsite,
        size: store.companySize,
      },
      documents: store.pastWinContext.trim()
        ? [{ doc_type: "win_loss", title: "Past wins", content: store.pastWinContext }]
        : [],
      icp: {
        target_industries: store.icpIndustries,
        company_size_min: Number(store.icpSizeMin) || 10,
        company_size_max: Number(store.icpSizeMax) || 5000,
        titles_targeted: store.icpTitles,
        geographies: store.icpGeographies,
        tech_stack_keywords: store.icpTechKeywords,
        offer_description: store.offerDescription,
      },
      signal_types: store.selectedSignalTypes,
    });
    store.reset();
    router.push("/app");
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      {/* Progress rail */}
      <ol className="mb-8 flex items-center gap-1">
        {STEPS.map((label, index) => {
          const stepNumber = index + 1;
          const state =
            stepNumber < store.step ? "done" : stepNumber === store.step ? "active" : "todo";
          return (
            <li key={label} className="flex flex-1 flex-col gap-1.5">
              <span
                className={`h-1 rounded ${
                  state === "done"
                    ? "bg-nexus-emerald"
                    : state === "active"
                      ? "bg-nexus-cyan"
                      : "bg-nexus-border"
                }`}
              />
              <span
                className={`hidden text-[10px] uppercase tracking-wider sm:block ${
                  state === "active" ? "text-nexus-cyan" : "text-nexus-muted"
                }`}
              >
                {label}
              </span>
            </li>
          );
        })}
      </ol>

      <div className="nexus-card p-6">
        {store.step === 1 && (
          <StepShell
            title="Tell NEXUS who you are"
            subtitle="Basics first. This anchors everything the Brain learns about you."
          >
            <Field label="Company name">
              <input
                className="nexus-input"
                value={store.companyName}
                onChange={(e) => store.setField("companyName", e.target.value)}
                placeholder="Acme Advisory"
              />
            </Field>
            <Field label="Website">
              <input
                className="nexus-input"
                value={store.companyWebsite}
                onChange={(e) => store.setField("companyWebsite", e.target.value)}
                placeholder="acmeadvisory.com"
              />
            </Field>
            <Field label="Team size">
              <div className="flex flex-wrap gap-1.5">
                {["Just me", "2-10", "11-50", "50+"].map((option) => (
                  <Chip
                    key={option}
                    active={store.companySize === option}
                    onClick={() => store.setField("companySize", option)}
                  >
                    {option}
                  </Chip>
                ))}
              </div>
            </Field>
          </StepShell>
        )}

        {store.step === 2 && (
          <StepShell
            title="What do you sell?"
            subtitle="One honest paragraph. The Outreach Writer uses this to position every message."
          >
            <textarea
              className="nexus-input min-h-[140px] resize-y"
              value={store.offerDescription}
              onChange={(e) => store.setField("offerDescription", e.target.value)}
              placeholder="We help mid-market logistics companies modernize operations after leadership changes. Typical engagement runs $45K to $250K over 3 to 6 months."
            />
          </StepShell>
        )}

        {store.step === 3 && (
          <StepShell
            title="Define your ideal client"
            subtitle="This drives the fit dimension of every NEXUS Score."
          >
            <Field label="Industries">
              <div className="flex flex-wrap gap-1.5">
                {INDUSTRY_OPTIONS.map((industry) => (
                  <Chip
                    key={industry}
                    active={store.icpIndustries.includes(industry)}
                    onClick={() => store.toggleListValue("icpIndustries", industry)}
                  >
                    {industry}
                  </Chip>
                ))}
              </div>
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Company size min">
                <input
                  type="number"
                  className="nexus-input"
                  value={store.icpSizeMin}
                  onChange={(e) => store.setField("icpSizeMin", e.target.value)}
                />
              </Field>
              <Field label="Company size max">
                <input
                  type="number"
                  className="nexus-input"
                  value={store.icpSizeMax}
                  onChange={(e) => store.setField("icpSizeMax", e.target.value)}
                />
              </Field>
            </div>
            <Field label="Decision-maker titles">
              <div className="flex flex-wrap gap-1.5">
                {TITLE_OPTIONS.map((title) => (
                  <Chip
                    key={title}
                    active={store.icpTitles.includes(title)}
                    onClick={() => store.toggleListValue("icpTitles", title)}
                  >
                    {title}
                  </Chip>
                ))}
              </div>
            </Field>
            <Field label="Geographies">
              <div className="flex flex-wrap gap-1.5">
                {GEO_OPTIONS.map((geo) => (
                  <Chip
                    key={geo}
                    active={store.icpGeographies.includes(geo)}
                    onClick={() => store.toggleListValue("icpGeographies", geo)}
                  >
                    {geo}
                  </Chip>
                ))}
              </div>
            </Field>
          </StepShell>
        )}

        {store.step === 4 && (
          <StepShell
            title="Teach the Brain your wins"
            subtitle="Paste past proposals, case studies, or win stories. More context means sharper coaching. You can add more later."
          >
            <textarea
              className="nexus-input min-h-[180px] resize-y"
              value={store.pastWinContext}
              onChange={(e) => store.setField("pastWinContext", e.target.value)}
              placeholder="We won a $180K engagement with a healthtech provider by reaching the incoming CIO three weeks after her appointment, before any RFP existed..."
            />
          </StepShell>
        )}

        {store.step === 5 && (
          <StepShell
            title="Pick your signals"
            subtitle="Which triggers matter for your business? You can change this anytime."
          >
            <div className="grid gap-2 sm:grid-cols-2">
              {ALL_SIGNAL_TYPES.map((type) => {
                const active = store.selectedSignalTypes.includes(type);
                return (
                  <button
                    key={type}
                    onClick={() => store.toggleListValue("selectedSignalTypes", type)}
                    className={`focus-ring flex items-center justify-between rounded border p-3 text-left ${
                      active
                        ? "border-nexus-cyan/60 bg-nexus-cyan/5"
                        : "border-nexus-border opacity-70 hover:opacity-100"
                    }`}
                  >
                    <SignalBadge type={type} />
                    <span className={`font-mono text-xs ${active ? "text-nexus-emerald" : "text-nexus-muted"}`}>
                      {active ? "ON" : "OFF"}
                    </span>
                  </button>
                );
              })}
            </div>
          </StepShell>
        )}

        {store.step === 6 && (
          <StepShell
            title="Review and launch"
            subtitle="NEXUS starts monitoring the moment you launch. First scored accounts arrive within the hour."
          >
            <dl className="space-y-3 text-sm">
              <ReviewRow label="Company" value={store.companyName || "Not set"} />
              <ReviewRow
                label="Offer"
                value={store.offerDescription ? `${store.offerDescription.slice(0, 120)}${store.offerDescription.length > 120 ? "..." : ""}` : "Not set"}
              />
              <ReviewRow
                label="ICP"
                value={`${store.icpIndustries.join(", ") || "any industry"} · ${store.icpSizeMin}-${store.icpSizeMax} employees · ${store.icpGeographies.join(", ") || "anywhere"}`}
              />
              <ReviewRow label="Titles" value={store.icpTitles.join(", ") || "Not set"} />
              <ReviewRow
                label="Context docs"
                value={store.pastWinContext.trim() ? "1 document ready to ingest" : "None yet"}
              />
              <ReviewRow
                label="Signals"
                value={`${store.selectedSignalTypes.length} of ${ALL_SIGNAL_TYPES.length} enabled`}
              />
            </dl>
          </StepShell>
        )}

        {/* Nav */}
        <div className="mt-6 flex items-center justify-between border-t border-nexus-border pt-4">
          <Button variant="secondary" onClick={store.back} disabled={store.step === 1}>
            Back
          </Button>
          {store.step < 6 ? (
            <Button onClick={store.next}>Continue</Button>
          ) : (
            <Button onClick={handleLaunch} disabled={launching}>
              {launching ? "Launching..." : "Launch NEXUS"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

function StepShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h1 className="font-display text-xl font-semibold text-nexus-text">{title}</h1>
      <p className="mt-1 text-sm text-nexus-muted">{subtitle}</p>
      <div className="mt-5 space-y-4">{children}</div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs font-medium text-nexus-text">{label}</span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`focus-ring rounded border px-2.5 py-1 text-xs font-medium ${
        active
          ? "border-nexus-cyan/60 bg-nexus-cyan/10 text-nexus-cyan"
          : "border-nexus-border text-nexus-muted hover:text-nexus-text"
      }`}
    >
      {children}
    </button>
  );
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-4">
      <dt className="w-28 shrink-0 text-xs uppercase tracking-wider text-nexus-muted">{label}</dt>
      <dd className="min-w-0 text-nexus-text">{value}</dd>
    </div>
  );
}
