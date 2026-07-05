import type { Metadata } from "next";
import { sans, mono, display } from "./fonts";
import "./globals.css";
import { QueryProvider } from "./query-provider";

export const metadata: Metadata = {
  title: "NEXUS Intelligence: Know Who's About to Buy",
  description:
    "NEXUS monitors 10,000+ daily signals and tells you which companies have budget, a problem, and no vendor, before they write the RFP.",
  metadataBase: new URL("https://nexus-intelligence.example.com"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable} ${display.variable}`}>
      <body className="nexus-bg-texture nexus-noise min-h-screen font-sans antialiased">
        <QueryProvider>
          <div className="relative z-10">{children}</div>
        </QueryProvider>
      </body>
    </html>
  );
}
