import Link from "next/link";
import { ArrowUpRight, CloudSun, Gauge, Orbit, Waves } from "lucide-react";

import { DataTypeBadge, DataUnavailable, SourceBadge } from "@/components/climate/source-ui";
import { formatClimateDate } from "@/lib/climate-format";
import type { ClimateOutlook } from "@/types/climate";

export function HomeEducation({ outlook }: { outlook: ClimateOutlook | null }) {
  return (
    <>
      <section className="home-meaning" data-home-scene data-scene-key="meaning">
        <header><p className="home-kicker">09 · What these signals mean</p><h2>Climate is a system of relationships, not a row of isolated metrics.</h2></header>
        <div className="home-meaning-flow">
          <article><span>01</span><Orbit aria-hidden="true" /><h3>Accumulation</h3><p>Greenhouse gases accumulate in the atmosphere and alter Earth&apos;s energy balance. Concentration and annual emissions describe related but different quantities.</p></article>
          <article><span>02</span><CloudSun aria-hidden="true" /><h3>Warming</h3><p>Temperature anomalies compare a period with a reference average. They make change visible without confusing anomaly values with absolute temperature.</p></article>
          <article><span>03</span><Waves aria-hidden="true" /><h3>Movement</h3><p>Oceans absorb and redistribute heat. Natural variability such as ENSO can reorganize ocean and atmospheric patterns from season to season.</p></article>
          <article><span>04</span><Gauge aria-hidden="true" /><h3>Probability</h3><p>Seasonal outlooks combine drivers and models to describe changed odds. They are broad guidance, not deterministic local weather promises.</p></article>
        </div>
      </section>

      <section className="home-timescales" data-home-scene data-scene-key="timescales">
        <div className="home-timescale-intro"><p className="home-kicker">10 · Four lenses on a changing planet</p><h2>Time changes the question.</h2><p>A hot day, an El Niño episode, and long-term warming can coexist. They describe different scales of Earth&apos;s behavior.</p></div>
        <dl>
          <div><dt><span>Hours → days</span>Weather</dt><dd>What the atmosphere is doing over short periods in a particular place.</dd></div>
          <div><dt><span>Years → decades</span>Climate</dt><dd>The patterns and ranges that emerge when weather is observed over long periods.</dd></div>
          <div><dt><span>Months → years</span>Climate variability</dt><dd>Recurring or irregular natural patterns—such as ENSO—that shift conditions around the usual range.</dd></div>
          <div><dt><span>Decades → longer</span>Climate change</dt><dd>Persistent shifts in average conditions, extremes, oceans, ice, and other parts of the climate system.</dd></div>
        </dl>
      </section>

      <section className="home-watch" data-home-scene data-scene-key="watch">
        <header><p className="home-kicker">11 · The forward view</p><h2>What we&apos;re watching.</h2>{outlook ? <p>{outlook.forecast_period.label} · WMO forecast issued {formatClimateDate(outlook.issue.issue_date)}</p> : <p>Current verified outlook unavailable.</p>}</header>
        {outlook ? <div className="home-watch-layout"><ol>{outlook.key_messages.map((message, index) => <li key={message}><span>{String(index + 1).padStart(2, "0")}</span><p>{message}<small>WMO · issued {formatClimateDate(outlook.issue.issue_date)} · {outlook.forecast_period.label}</small></p></li>)}</ol><aside><DataTypeBadge type="forecast" /><h3>How to read the outlook</h3><p>{outlook.methodology.outlook_meaning}</p><p>{outlook.methodology.tercile_explanation}</p><SourceBadge source={outlook.sources[0]} compact /></aside></div> : <DataUnavailable label="What we are watching" detail="No replacement forecast has been invented." />}
      </section>

      <nav className="home-public-paths" aria-label="Explore public climate content">
        <p className="home-kicker">Continue exploring</p>
        <Link href="/climate-now"><span>Climate Now</span><strong>Read the full source-backed briefing</strong><ArrowUpRight aria-hidden="true" /></Link>
        <Link href="/climate-now/enso"><span>El Niño</span><strong>Understand the Pacific signal</strong><ArrowUpRight aria-hidden="true" /></Link>
        <Link href="/outlooks"><span>Outlooks</span><strong>Read the seasonal forecast foundation</strong><ArrowUpRight aria-hidden="true" /></Link>
        <Link href="/explore"><span>Climate data</span><strong>Explore the public data foundation</strong><ArrowUpRight aria-hidden="true" /></Link>
        <Link href="/learn"><span>Climate science</span><strong>Build your understanding</strong><ArrowUpRight aria-hidden="true" /></Link>
        <Link href="/sdg/13"><span>SDG 13</span><strong>Understand Climate Action</strong><ArrowUpRight aria-hidden="true" /></Link>
      </nav>
    </>
  );
}
