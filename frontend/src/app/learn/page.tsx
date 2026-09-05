import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Learn", description: "Readable climate science explanations grounded in authoritative sources." };

export default function LearnPage() {
  return <PublicPageFoundation eyebrow="Climate knowledge" title="Understand a changing Earth." description="Long-form, readable explanations of climate systems, evidence, uncertainty, impacts, mitigation, and adaptation." questions={["What does the concept mean?", "What does the evidence show?", "Where does scientific certainty end?"]} />;
}
