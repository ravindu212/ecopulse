import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "ENSO", description: "Current ENSO observations, outlooks, uncertainty, and Pacific climate context." };

export default function EnsoPage() {
  return <PublicPageFoundation eyebrow="El Niño–Southern Oscillation" title="The Pacific shifts the odds." description="A Pacific-centered explanation of ENSO observations and outlooks, including Niño indices, probabilities, duration, and the limits of local impact inference." questions={["What is the ocean-atmosphere system doing?", "What do observations and forecasts show?", "How does ENSO shift risk without determining weather?"]} />;
}
