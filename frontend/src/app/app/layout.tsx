import type { Metadata } from "next";
import { AppSidebar } from "@/components/app/AppSidebar";
import { CostFooter } from "@/components/app/CostFooter";

export const metadata: Metadata = {
  title: "NEXUS Command Center",
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <main className="min-h-0 flex-1">{children}</main>
        <CostFooter />
      </div>
    </div>
  );
}
