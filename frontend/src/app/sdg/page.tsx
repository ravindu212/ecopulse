import type { Metadata } from "next";
import { PublicPageFoundation } from "@/components/editorial/public-page-foundation";

export const metadata: Metadata = { title: "Sustainable Development Goals", description: "A readable independent guide to all 17 UN Sustainable Development Goals." };

export default function SdgPage() {
  return <PublicPageFoundation eyebrow="The 2030 Agenda" title="Seventeen connected goals." description="A readable independent guide to the Sustainable Development Goals and the relationships between climate, health, equity, cities, ecosystems, and development." questions={["What does each goal address?", "How are the goals connected?", "Where does climate action fit?"]} />;
}
