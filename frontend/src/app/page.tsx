import type { Metadata } from "next";
import { connection } from "next/server";

import { HomeAction } from "@/components/home/home-action";
import { HomeDataStory } from "@/components/home/home-data-story";
import { HomeEducation } from "@/components/home/home-education";
import { HomeMotionLoader } from "@/components/home/home-motion-loader";
import { SiteHeader } from "@/components/layout/site-header";
import { getClimateCO2, getClimateENSO, getClimateOutlook, getClimateOverview, getEarthEvents } from "@/lib/api";
import "./home.css";

export const metadata: Metadata = {
  title: { absolute: "EcoPulse | Earth signals, clearly observed" },
  description: "A public climate observatory for current atmospheric, ocean, temperature, ENSO, sea-ice, outlook, and Earth-event signals—with an optional pathway to practical personal action.",
  openGraph: {
    title: "EcoPulse | Earth signals, clearly observed",
    description: "Explore source-backed climate signals, understand how Earth systems connect, and choose an optional personal climate pathway.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "EcoPulse | Earth signals, clearly observed",
    description: "A cinematic, source-backed public climate observatory and optional personal action platform.",
  },
};

function settledValue<T>(result: PromiseSettledResult<T>): T | null {
  return result.status === "fulfilled" ? result.value : null;
}

export default async function Home() {
  await connection();
  const results = await Promise.allSettled([
    getClimateOverview(),
    getClimateCO2(),
    getClimateENSO(),
    getClimateOutlook(),
    getEarthEvents({ days: 30, limit: 8 }),
  ] as const);

  return (
    <main className="home-observatory" data-home-observatory>
      <div className="home-navigation"><SiteHeader /></div>
      <HomeDataStory
        overview={settledValue(results[0])}
        co2={settledValue(results[1])}
        enso={settledValue(results[2])}
        outlook={settledValue(results[3])}
        events={settledValue(results[4])}
      />
      <HomeEducation />
      <HomeAction />
      <HomeMotionLoader />
    </main>
  );
}
