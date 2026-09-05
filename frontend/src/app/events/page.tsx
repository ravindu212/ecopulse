import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Earth Events", description: "Current significant Earth events without unsupported climate attribution." };

export default function EventsPage() {
  return <PublicPageFoundation eyebrow="Current Earth events" title="Events are not attribution." description="A geographic view of significant natural events with category, date, location, and original source—without claiming climate causation where attribution evidence is absent." questions={["What event was detected and where?", "Which organization reported it?", "What does detection not prove?"]} />;
}
