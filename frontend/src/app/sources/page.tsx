import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Sources and Methodology", description: "Scientific sources, update cadence, freshness, methods, and limitations used by EcoPulse." };

export default function SourcesPage() {
  return <PublicPageFoundation eyebrow="Sources and methodology" title="Every important number should be inspectable." description="The source register will document publishers, original datasets, issue and observation dates, data types, cache freshness, methodology, and known limitations." questions={["Who published the source?", "When was it observed, issued, and fetched?", "How should the value be interpreted?"]} />;
}
