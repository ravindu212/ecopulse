import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Climate Now", description: "A source-first view of the current state of Earth's climate system." };

export default function ClimateNowPage() {
  return <PublicPageFoundation eyebrow="Climate system status" title="What is happening now?" description="A source-first briefing across observed conditions, scientific analysis, and signals worth watching next." questions={["What has been observed?", "Which signals are analysis or forecast?", "When was each source issued or updated?"]} />;
}
