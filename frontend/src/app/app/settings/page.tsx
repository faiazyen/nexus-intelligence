"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { useICPProfile, useUpdateICP, usePlanUsage } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import type { ICPProfile } from "@/lib/types";

function listToText(list: string[]): string {
  return list.join(", ");
}

function textToList(text: string): string[] {
  return text
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function SettingsPage() {
  const icp = useICPProfile();
  const updateICP = useUpdateICP();
  const plan = usePlanUsage();

  const [form, setForm] = useState<ICPProfile | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (icp.data && form === null) {
      setForm(icp.data);
    }
  }, [icp.data, form]);

  const handleSave = () => {
    if (!form) return;
    updateICP.mutate(form, {
      onSuccess: () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      },
    });
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <header className="mb-6">
        <h1 className="font-display text-2xl font-semibold text-nexus-text">Settings</h1>
        <p className="mt-1 text-sm text-nexus-muted">
          Your ICP drives the fit dimension of every NEXUS Score. Keep it sharp.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        {/* ICP editor */}
        <section className="nexus-card p-5">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">
            ICP profile
          </h2>
          {!form ? (
            <div className="mt-4">
              <SkeletonCard />
            </div>
          ) : (
            <div className="mt-4 space-y-4">
              <Field label="Target industries" hint="comma separated">
                <input
                  className="nexus-input"
                  value={listToText(form.targetIndustries)}
                  onChange={(e) => setForm({ ...form, targetIndustries: textToList(e.target.value) })}
                />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Field label="Company size min">
                  <input
                    type="number"
                    className="nexus-input"
                    value={form.companySizeMin}
                    onChange={(e) => setForm({ ...form, companySizeMin: Number(e.target.value) || 0 })}
                  />
                </Field>
                <Field label="Company size max">
                  <input
                    type="number"
                    className="nexus-input"
                    value={form.companySizeMax}
                    onChange={(e) => setForm({ ...form, companySizeMax: Number(e.target.value) || 0 })}
                  />
                </Field>
              </div>
              <Field label="Titles targeted" hint="comma separated">
                <input
                  className="nexus-input"
                  value={listToText(form.titlesTargeted)}
                  onChange={(e) => setForm({ ...form, titlesTargeted: textToList(e.target.value) })}
                />
              </Field>
              <Field label="Geographies" hint="comma separated">
                <input
                  className="nexus-input"
                  value={listToText(form.geographies)}
                  onChange={(e) => setForm({ ...form, geographies: textToList(e.target.value) })}
                />
              </Field>
              <Field label="Tech stack keywords" hint="comma separated">
                <input
                  className="nexus-input"
                  value={listToText(form.techKeywords)}
                  onChange={(e) => setForm({ ...form, techKeywords: textToList(e.target.value) })}
                />
              </Field>
              <Field label="Offer description" hint="what you sell, in one paragraph">
                <textarea
                  className="nexus-input min-h-[96px] resize-y"
                  value={form.offerDescription}
                  onChange={(e) => setForm({ ...form, offerDescription: e.target.value })}
                />
              </Field>
              <div className="flex items-center gap-3">
                <Button onClick={handleSave} disabled={updateICP.isPending}>
                  {updateICP.isPending ? "Saving..." : "Save ICP"}
                </Button>
                {saved && <span className="text-xs text-nexus-emerald">Saved.</span>}
              </div>
            </div>
          )}
        </section>

        {/* Plan usage */}
        <section className="nexus-card h-fit p-5">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-nexus-muted">
            Plan &amp; usage
          </h2>
          {plan.data ? (
            <div className="mt-4 space-y-4 text-sm">
              <div className="flex items-baseline justify-between">
                <span className="font-semibold text-nexus-cyan">{plan.data.planName}</span>
                <span className="text-xs text-nexus-muted">renews {plan.data.renewsOn}</span>
              </div>
              <UsageBar
                label="Accounts monitored"
                used={plan.data.accountsMonitored}
                limit={plan.data.accountsLimit}
              />
              <UsageBar
                label="Action Queue credits"
                used={plan.data.actionQueueCreditsUsed}
                limit={plan.data.actionQueueCreditsLimit}
              />
              <UsageBar label="Seats" used={plan.data.seatsUsed} limit={plan.data.seatsLimit} />
            </div>
          ) : (
            <div className="mt-4">
              <SkeletonCard />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="flex items-baseline gap-2">
        <span className="text-xs font-medium text-nexus-text">{label}</span>
        {hint && <span className="text-[11px] text-nexus-muted">{hint}</span>}
      </span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}

function UsageBar({ label, used, limit }: { label: string; used: number; limit: number | null }) {
  const pct = limit ? Math.min(100, Math.round((used / limit) * 100)) : 0;
  return (
    <div>
      <div className="flex justify-between text-xs">
        <span className="text-nexus-muted">{label}</span>
        <span className="font-mono tabular-nums text-nexus-text">
          {formatNumber(used)} / {limit === null ? "∞" : formatNumber(limit)}
        </span>
      </div>
      <div className="mt-1 h-1.5 overflow-hidden rounded bg-nexus-border">
        <div
          className={`h-full rounded ${pct > 85 ? "bg-nexus-amber" : "bg-nexus-cyan"}`}
          style={{ width: limit === null ? "8%" : `${pct}%` }}
        />
      </div>
    </div>
  );
}
