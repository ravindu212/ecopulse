import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Climate Indicators", description: "Major climate indicators, historical context, sources, units, and baselines." };

export default function IndicatorsPage() {
  return <PublicPageFoundation eyebrow="Observed indicators" title="Change, measured over time." description="Atmospheric carbon dioxide, temperature, ocean heat, sea level, and sea ice shown with the context required to interpret them responsibly." questions={["What exactly is measured?", "How has it changed over time?", "Which baseline and method apply?"]} />;
}
