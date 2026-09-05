import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "SDG 13: Climate Action", description: "An independent guide to UN Sustainable Development Goal 13 and its connections." };

export default function Sdg13Page() {
  return <PublicPageFoundation eyebrow="Sustainable Development Goal 13" title="Climate action is a shared system." description="An independent explanation of SDG 13, its targets, resilience, education, mitigation, adaptation, and relationships with the other global goals." questions={["What does SDG 13 call for?", "How does it connect to other goals?", "Where can personal action contribute?"]} />;
}
