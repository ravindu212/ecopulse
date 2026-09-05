import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Climate Outlooks", description: "Probabilistic seasonal outlooks with uncertainty and model context." };

export default function OutlooksPage() {
  return <PublicPageFoundation eyebrow="Forecasts and outlooks" title="What might happen next?" description="Seasonal model guidance presented as probability—not deterministic local weather—with initialization, period, ensemble, and uncertainty made visible." questions={["What period does the outlook cover?", "Which model and ensemble produced it?", "What can and cannot be inferred locally?"]} />;
}
