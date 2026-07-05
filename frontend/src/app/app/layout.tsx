import type { Metadata } from "next";
import { AppSidebar } from "@/components/app/AppSidebar";

export const metadata: Metadata = {
  title: "NEXUS Command Center",
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
