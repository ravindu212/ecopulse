import Image from "next/image";
import Link from "next/link";
import { ArrowDown, ArrowUpRight, CloudRain, Snowflake, ThermometerSun, Waves, Wind } from "lucide-react";
import type { CSSProperties } from "react";

import { DataFreshness, DataTypeBadge, DataUnavailable, SourceBadge } from "@/components/climate/source-ui";
import { formatClimateDate, formatProbability, formatSigned, humanize } from "@/lib/climate-format";
import type { ClimateCO2, ClimateENSO, ClimateOutlook, ClimateOverview, EarthEvent, EarthEvents } from "@/types/climate";
import { SeriesPlot } from "./series-plot";

type HomeClimateData = {
  overview: ClimateOverview | null;
  co2: ClimateCO2 | null;
  enso: ClimateENSO | null;
  outlook: ClimateOutlook | null;
  events: EarthEvents | null;
};

function HeroSignal({ label, value, detail, type }: { label: string; value: string; detail: string; type: "estimate" | "analysis" | "forecast" }) {
  return (
    <li>
      <div><span>{label}</span><DataTypeBadge type={type} /></div>
      <strong>{value}</strong>
      <small>{detail}</small>
    </li>
  );
}

function EventPoint({ event, index }: { event: EarthEvent; index: number }) {
  const coordinates = event.latest_geometry?.coordinates;
  const longitude = coordinates?.[0];
  const latitude = coordinates?.[1];
  const x = typeof longitude === "number" ? ((longitude + 180) / 360) * 100 : 12 + index * 16;
  const y = typeof latitude === "number" ? ((90 - latitude) / 180) * 100 : 30 + (index % 2) * 28;
  const href = event.sources[0]?.url ?? event.eonet_url;

  return (
    <li style={{ "--event-x": `${x}%`, "--event-y": `${y}%` } as CSSProperties}>
      <span aria-hidden="true" />
      <div>
        <small>{event.categories[0]?.title ?? "Earth event"}</small>
        <strong>{event.title}</strong>
        {event.latest_geometry?.date ? <time dateTime={event.latest_geometry.date}>{formatClimateDate(event.latest_geometry.date)}</time> : null}
        {href ? <a href={href} target="_blank" rel="noreferrer">Source <ArrowUpRight size={12} aria-hidden="true" /></a> : null}
      </div>
    </li>
  );
}

export function HomeDataStory({ overview, co2, enso, outlook, events }: HomeClimateData) {
  const temperature = overview?.global_temperature ?? null;
  const heroTimestamp = overview?.generated_at ?? null;
  const currentCO2 = co2?.latest;
  const currentNino = enso?.observations.latest_nino34;
  const eventSelection = events?.events.slice(0, 5) ?? [];

  return (
    <>
      <section className="home-hero" aria-labelledby="home-title">
        <div className="home-hero-earth" aria-hidden="true">
          <Image
            src="/media/home/nasa-blue-marble-alpha.webp"
            alt=""
            width={1600}
            height={1600}
            sizes="(max-width: 768px) 100vw, 68vw"
            fetchPriority="high"
          />
          <span className="home-orbit home-orbit-one" /><span className="home-orbit home-orbit-two" />
        </div>
        <div className="home-hero-copy">
          <p className="home-kicker">Earth observatory · source-backed climate intelligence</p>
          <h1 id="home-title"><span>The planet</span><span>is always</span><span>sending signals.</span></h1>
          <p className="home-hero-deck">Read what the atmosphere, ocean, ice, and Pacific are showing now—then decide where your own climate pathway begins.</p>
        </div>
        <ol className="home-hero-signals" aria-label="Current climate signals">
          <HeroSignal label="Atmospheric CO₂" value={currentCO2 ? `${currentCO2.value.toFixed(2)} ppm` : "Unavailable"} detail={currentCO2 ? formatClimateDate(currentCO2.observed_at) : "NOAA source unavailable"} type="estimate" />
          <HeroSignal label="ENSO state" value={enso?.status.alert_status ?? "Unavailable"} detail={enso ? `Issued ${formatClimateDate(enso.status.issued_at)}` : "NOAA analysis unavailable"} type="analysis" />
          <HeroSignal label="Global temperature" value={temperature?.latest_anomaly ? `${formatSigned(temperature.latest_anomaly.value, 3)} °C` : "Unavailable"} detail={temperature?.latest_anomaly?.period ?? "NOAA analysis unavailable"} type="analysis" />
          <HeroSignal label="Seasonal outlook" value={outlook?.forecast_period.label ?? "Unavailable"} detail={outlook ? `Issued ${formatClimateDate(outlook.issue.issue_date)}` : "WMO forecast unavailable"} type="forecast" />
        </ol>
        <div className="home-hero-foot">
          <p>{heroTimestamp ? `Briefing assembled ${formatClimateDate(heroTimestamp, { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" })} UTC` : "Briefing time unavailable"}</p>
          <a href="#signals">Follow the signals <ArrowDown size={15} aria-hidden="true" /></a>
        </div>
      </section>

      <section id="signals" className="home-story-prologue">
        <p className="home-kicker">01 · Earth right now</p>
        <h2>Different instruments.<br />Different clocks.<br /><em>One connected system.</em></h2>
        <p>Climate is not one number. Concentrations, anomalies, ocean conditions, natural variability, ice, forecasts, and events each answer a different question.</p>
      </section>

      <section className="home-system-journey" data-system-journey data-active-scene="co2" aria-label="Scroll-driven climate signal sequence">
        <div className="home-system-visual" aria-hidden="true">
          <div className="home-atmosphere-field" />
          <div className="home-pacific-band"><span /><span /><span /></div>
          <div className="home-system-disc"><div /></div>
          <p><span>ATM</span><span>OCEAN</span><span>PACIFIC</span><span>OUTLOOK</span></p>
        </div>

        <div className="home-system-chapters">
          <article className="home-signal-scene home-co2-scene" data-home-scene data-scene-key="co2">
            <header><span>02</span><p>Atmosphere · estimated global trend</p></header>
            <div className="home-scene-grid">
              <div><DataTypeBadge type="estimate" /><h2>Carbon in the air has a timeline.</h2><p>Atmospheric CO₂ concentration is the amount present in the atmosphere. It is not the same measurement as annual emissions.</p></div>
              {currentCO2 && co2.series.length ? <div className="home-data-focus"><strong>{currentCO2.value.toFixed(2)}</strong><span>parts per million</span><time dateTime={currentCO2.observed_at}>Observed {formatClimateDate(currentCO2.observed_at)}</time><SeriesPlot points={co2.series} tone="carbon" label="Recent atmospheric carbon dioxide series" summary={`The bounded NOAA series ends at ${currentCO2.value.toFixed(2)} ppm on ${formatClimateDate(currentCO2.observed_at)}.`} /><SourceBadge source={co2.source} compact /></div> : <DataUnavailable label="Atmospheric CO₂" detail="The story continues with other verified signals." />}
            </div>
          </article>

          <article className="home-signal-scene home-temperature-scene" data-home-scene data-scene-key="temperature">
            <header><span>03</span><p>Global temperature · analysis</p></header>
            <div className="home-scene-grid">
              <div><DataTypeBadge type="analysis" /><h2>Warmth is measured against a reference climate.</h2><p>A temperature anomaly is a difference from an average over a stated baseline—not Earth&apos;s absolute temperature.</p></div>
              {temperature?.latest_anomaly && temperature.historical_series.length ? <div className="home-data-focus"><strong>{formatSigned(temperature.latest_anomaly.value, 3)}°C</strong><span>relative to {temperature.baseline}</span><time dateTime={temperature.latest_anomaly.observed_at}>{temperature.latest_anomaly.period}</time><SeriesPlot points={temperature.historical_series} tone="warm" label="Recent global surface temperature anomaly series" summary={`The latest NOAA monthly anomaly is ${formatSigned(temperature.latest_anomaly.value, 3)} degrees Celsius for ${temperature.latest_anomaly.period}.`} /><SourceBadge source={temperature.source} compact /></div> : <DataUnavailable label="Global temperature analysis" />}
            </div>
          </article>

          <article className="home-signal-scene home-ocean-scene" data-home-scene data-scene-key="ocean">
            <header><span>04</span><p>Ocean · issued analysis</p></header>
            <div className="home-scene-grid">
              <div><DataTypeBadge type="analysis" /><h2>The ocean stores and moves enormous amounts of heat.</h2><p>Ocean conditions shape weather, ecosystems, sea ice, and how warmth moves through the climate system.</p></div>
              {overview ? <div className="home-ocean-reading"><Waves aria-hidden="true" /><small>{overview.ocean.reference_period}</small><h3>{overview.ocean.headline}</h3><p>{overview.ocean.summary}</p><SourceBadge source={overview.ocean.source} compact /></div> : <DataUnavailable label="Copernicus ocean context" />}
            </div>
          </article>

          <article className="home-signal-scene home-enso-scene" data-home-scene data-scene-key="enso">
            <header><span>05</span><p>Pacific · observation → analysis → outlook</p></header>
            <div className="home-scene-grid">
              <div><h2>The tropical Pacific changes the rhythm.</h2><p>ENSO is a recurring ocean–atmosphere pattern. The Niño 3.4 index describes observed sea-surface temperature departures in a central Pacific region.</p></div>
              {enso ? <div className="home-enso-stack">
                <div className="home-evidence home-evidence-observed"><DataTypeBadge type="observation" /><strong>{currentNino ? `${formatSigned(currentNino.value)} °C` : "Unavailable"}</strong><p>Niño 3.4 · {currentNino?.period ?? "No current observation"}</p><DataFreshness freshness={enso.observation_freshness} /></div>
                <div className="home-evidence home-evidence-analysis"><DataTypeBadge type="analysis" /><strong>{enso.status.alert_status}</strong><p>{enso.status.headline}</p><time dateTime={enso.status.issued_at}>Issued {formatClimateDate(enso.status.issued_at)}</time></div>
                <div className="home-evidence home-evidence-forecast"><DataTypeBadge type="forecast" /><strong>{enso.outlook.wmo.headline}</strong><p>{enso.outlook.wmo.summary}</p></div>
                {enso.observations.nino34_series.length ? <SeriesPlot points={enso.observations.nino34_series} tone="warm" label="Recent Niño 3.4 anomaly series" summary={currentNino ? `The latest plotted Niño 3.4 anomaly is ${formatSigned(currentNino.value)} degrees Celsius for ${currentNino.period}.` : "No current Niño 3.4 point is available."} /> : null}
                <SourceBadge source={enso.observations.source} compact />
              </div> : <DataUnavailable label="ENSO intelligence" />}
            </div>
          </article>

          <article className="home-signal-scene home-outlook-scene" data-home-scene data-scene-key="outlook">
            <header><span>06</span><p>What we are watching next · forecast</p></header>
            <div className="home-scene-grid">
              <div><DataTypeBadge type="forecast" /><h2>Forecasts describe shifts in probability.</h2><p>Seasonal outlooks summarize broad conditions over months. They are not daily weather predictions for a specific place.</p></div>
              {outlook ? <div className="home-outlook-reading"><h3>{outlook.forecast_period.label}</h3><p>Issued {formatClimateDate(outlook.issue.issue_date)} · baseline {outlook.baseline}</p><div className="home-driver-pair"><div><Wind aria-hidden="true" /><small>ENSO driver</small><strong>{humanize(outlook.oceanic_drivers.enso.phase)}</strong><p>{outlook.oceanic_drivers.enso.status}</p></div><div><Waves aria-hidden="true" /><small>IOD driver</small><strong>{outlook.oceanic_drivers.iod ? humanize(outlook.oceanic_drivers.iod.phase) : "Not supplied"}</strong><p>{outlook.oceanic_drivers.iod?.status ?? "No verified IOD field in this issue."}</p></div></div><div className="home-tendency-pair"><div><ThermometerSun aria-hidden="true" /><span>Temperature</span><strong>{outlook.temperature.headline}</strong>{outlook.temperature.tendencies[0] ? <em>{formatProbability(outlook.temperature.tendencies[0].probability, outlook.temperature.tendencies[0].qualifier)}</em> : null}</div><div><CloudRain aria-hidden="true" /><span>Precipitation</span><strong>{outlook.precipitation.headline}</strong>{outlook.precipitation.tendencies[0] ? <em>{formatProbability(outlook.precipitation.tendencies[0].probability, outlook.precipitation.tendencies[0].qualifier)}</em> : null}</div></div><SourceBadge source={outlook.sources[0]} compact /></div> : <DataUnavailable label="WMO seasonal outlook" detail="Observed chapters remain available." />}
            </div>
          </article>
        </div>
      </section>

      <section className="home-ice-scene" data-home-scene data-scene-key="ice">
        <div className="home-ice-image"><Image src="/media/home/nasa-arctic-mosaic.webp" alt="A satellite mosaic looking down over the Arctic, with sea ice, cloud systems, and northern landmasses visible around the pole." width={1800} height={1200} sizes="100vw" loading="lazy" /><p>Context image · Arctic mosaic, September 2012 · NASA Earth Observatory</p></div>
        <div className="home-ice-copy"><p className="home-kicker">07 · Polar context</p><h2>Ice moves with the seasons. Context compares like with like.</h2>{overview ? <div className="home-polar-pair"><article><Snowflake aria-hidden="true" /><span>Arctic · {overview.sea_ice.arctic.reference_period}</span><strong>{overview.sea_ice.arctic.headline}</strong><p>{overview.sea_ice.arctic.summary}</p></article><article><Snowflake aria-hidden="true" /><span>Antarctic · {overview.sea_ice.antarctic.reference_period}</span><strong>{overview.sea_ice.antarctic.headline}</strong><p>{overview.sea_ice.antarctic.summary}</p></article><SourceBadge source={overview.latest_bulletin.source} compact /></div> : <DataUnavailable label="Monthly sea-ice analysis" />}</div>
      </section>

      <section className="home-events-scene" data-home-scene data-scene-key="events">
        <header><p className="home-kicker">08 · Current Earth events</p><h2>Location is context.<br /><em>Detection is not attribution.</em></h2><p>NASA EONET identifies recent natural events and their coordinates. An event appearing here does not prove that climate change caused it.</p></header>
        {events ? <><div className="home-event-field" aria-label="Selected recent NASA Earth events"><div className="home-event-grid" aria-hidden="true" /><ol>{eventSelection.map((event, index) => <EventPoint event={event} index={index} key={event.id} />)}</ol></div><p className="home-event-disclaimer">{events.attribution_disclaimer}</p><SourceBadge source={events.source} compact /></> : <DataUnavailable label="NASA Earth Events" detail="No synthetic events have been substituted." />}
        <Link className="home-text-link" href="/climate-now">Open the complete Climate Now briefing <ArrowUpRight size={15} aria-hidden="true" /></Link>
      </section>
    </>
  );
}
