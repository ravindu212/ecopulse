import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Explore Climate Data", description: "Interactive, mobile-safe exploration of authoritative climate datasets." };

export default function ExplorePage() {
  return <PublicPageFoundation eyebrow="Interactive data" title="Read the signal, not the spectacle." description="Explore climate indicators across time while retaining exact values, units, baselines, methodology, and accessible text alternatives." questions={["How has the indicator changed?", "What baseline and unit are used?", "Where can the original dataset be opened?"]} />;
}
