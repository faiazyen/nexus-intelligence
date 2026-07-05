import { IBM_Plex_Mono, IBM_Plex_Sans, Fraunces } from "next/font/google";

export const sans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

// Display serif used only for marketing headlines: gives NEXUS an editorial,
// declarative voice that contrasts with the dense terminal typography in-app.
export const display = Fraunces({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-display",
  display: "swap",
});
