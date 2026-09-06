import type { Metadata } from "next";
import Link from "next/link";
import { connection } from "next/server";
import { Activity, ArrowUpRight, CalendarDays, CloudRain, Gauge, Globe2, Snowflake, ThermometerSun, Waves, Wind } from "lucide-react";

import { CO2Chart, ENSOChart, TemperatureChart } from "@/components/climate/climate-charts";
import { DataFreshness, DataTypeBadge, DataUnavailable, MethodologyNote, SourceBadge, SourcePanel } from "@/components/climate/source-ui";
import { StoryReveal } from "@/components/climate/story-motion";
import { SiteHeader } from "@/components/layout/site-header";
import { formatClimateDate, formatProbability, formatSigned, humanize } from "@/lib/climate-format";
import { getClimateCO2, getClimateENSO, getClimateOutlook, getClimateOverview, getEarthEvents } from "@/lib/api";
import type { ClimateDataType, ClimateFreshness } from "@/types/climate";

export const metadata: Metadata = {
  title: { absolute: "Climate Now | EcoPulse" },
  description: "A source-backed public briefing across atmospheric CO₂, ocean and temperature signals, ENSO, sea ice, seasonal outlooks, and current Earth events.",
};

function settledValue<T>(result: PromiseSettledResult<T>): T | null {
  return result.status === "fulfilled" ? result.value : null;
}

function Signal({ label, value, context, type, freshness }: { label: string; value: string | null; context: string; type: ClimateDataType; freshness: ClimateFreshness }) {
  return <li className="climate-signal"><div><span>{label}</span><DataTypeBadge type={type} /></div><strong>{value ?? "Unavailable"}</strong><p>{context}</p><DataFreshness freshness={value ? freshness : "unavailable"} issued={type === "analysis"} /></li>;
}

function SectionLead({ index, eyebrow, title, children }: { index: string; eyebrow: string; title: string; children: React.ReactNode }) {
  return <header className="climate-section-lead"><p><span>{index}</span>{eyebrow}</p><h2>{title}</h2><div>{children}</div></header>;
}

function coordinatesLabel(coordinates: unknown[]) {
  const longitude = coordinates[0];
  const latitude = coordinates[1];
  if (typeof longitude !== "number" || typeof latitude !== "number") return null;
  return `${Math.abs(latitude).toFixed(2)}°${latitude >= 0 ? "N" : "S"}, ${Math.abs(longitude).toFixed(2)}°${longitude >= 0 ? "E" : "W"}`;
}

export default async function ClimateNowPage() {
  await connection();
  const results = await Promise.allSettled([getClimateOverview(), getClimateCO2(), getClimateENSO(), getClimateOutlook(), getEarthEvents({ days: 30, limit: 8 })] as const);
  const overview = settledValue(results[0]);
  const co2 = settledValue(results[1]);
  const enso = settledValue(results[2]);
  const outlook = settledValue(results[3]);
  const events = settledValue(results[4]);
  const temperature = overview?.global_temperature ?? null;
  const bulletin = overview?.latest_bulletin ?? null;

  return (
    <main className="climate-now-shell">
      <div className="climate-now-nav"><SiteHeader /></div>

      <section className="climate-now-hero" aria-labelledby="climate-now-title">
        <div className="climate-orbit" aria-hidden="true"><span /><span /><span /></div>
        <div className="climate-hero-copy"><p className="climate-kicker">Climate system status · Source-backed briefing</p><h1 id="climate-now-title">Climate<br />Now</h1><p>A source-backed view of the signals shaping Earth&apos;s climate system.</p></div>
        <aside className="climate-hero-meta">
          <div><span>Briefing generated</span><strong>{overview ? formatClimateDate(overview.generated_at, { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }) : "Timestamp unavailable"}</strong></div>
          <p>Indicators update at different frequencies. Observation, analysis, and forecast dates are shown individually; this page is not described as wholly live.</p>
          <Link href="/sources">Sources &amp; methodology <ArrowUpRight size={15} aria-hidden="true" /></Link>
        </aside>
      </section>

      <section className="climate-signal-band" aria-labelledby="signal-heading">
        <div className="climate-band-label"><span>01</span><h2 id="signal-heading">Current signal strip</h2><p>Different clocks. One climate system.</p></div>
        <ol className="climate-signals">
          <Signal label="Atmospheric CO₂" value={co2?.latest ? `${co2.latest.value.toFixed(2)} ppm` : null} context={co2?.latest ? `Observed ${formatClimateDate(co2.latest.observed_at)}` : "NOAA observation unavailable"} type="estimate" freshness={co2?.status ?? "unavailable"} />
          <Signal label="ENSO" value={enso?.status.alert_status ?? null} context={enso ? `Analysis issued ${formatClimateDate(enso.status.issued_at)}` : "NOAA analysis unavailable"} type="analysis" freshness={enso?.status.source.freshness ?? "unavailable"} />
          <Signal label="Global temperature" value={temperature?.latest_anomaly ? `${formatSigned(temperature.latest_anomaly.value, 3)} °C` : null} context={temperature?.latest_anomaly ? `${temperature.latest_anomaly.period} · vs ${temperature.baseline}` : "Monthly analysis unavailable"} type="analysis" freshness={temperature?.freshness ?? "unavailable"} />
          <Signal label="Ocean" value={overview?.ocean.headline ?? null} context={overview?.ocean.reference_period ?? "Copernicus analysis unavailable"} type="analysis" freshness={overview?.ocean.source.freshness ?? "unavailable"} />
          <Signal label="Arctic sea ice" value={overview?.sea_ice.arctic.rank ? `#${overview.sea_ice.arctic.rank} ${overview.sea_ice.arctic.rank_qualifier ?? "rank"}` : overview?.sea_ice.arctic.headline ?? null} context={overview?.sea_ice.arctic.reference_period ?? "Monthly analysis unavailable"} type="analysis" freshness={overview?.sea_ice.arctic.source.freshness ?? "unavailable"} />
          <Signal label="Antarctic sea ice" value={overview?.sea_ice.antarctic.rank ? `#${overview.sea_ice.antarctic.rank} ${overview.sea_ice.antarctic.rank_qualifier ?? "rank"}` : overview?.sea_ice.antarctic.headline ?? null} context={overview?.sea_ice.antarctic.reference_period ?? "Monthly analysis unavailable"} type="analysis" freshness={overview?.sea_ice.antarctic.source.freshness ?? "unavailable"} />
          <Signal label="Seasonal outlook" value={outlook?.forecast_period.label ?? null} context={outlook ? `Issued ${formatClimateDate(outlook.issue.issue_date)} · ${humanize(outlook.forecast_period.validity)}` : "WMO forecast unavailable"} type="forecast" freshness={outlook?.sources[0]?.freshness ?? "unavailable"} />
          <Signal label="Earth events" value={events ? `${events.count} returned` : null} context={events ? `Fetched ${formatClimateDate(events.fetched_at)}` : "NASA EONET unavailable"} type="observation" freshness={events?.freshness ?? "unavailable"} />
        </ol>
      </section>

      <StoryReveal className="climate-story-section climate-co2-story">
        <SectionLead index="02" eyebrow="Atmosphere" title="Carbon in the air has a timeline."><p>Atmospheric CO₂ concentration measures how much carbon dioxide is present in the atmosphere. It is different from the amount emitted during a year.</p></SectionLead>
        <div className="climate-story-content">{co2?.latest && co2.series.length > 0 ? <>
          <div className="climate-primary-reading"><span>Latest concentration</span><strong>{co2.latest.value.toFixed(2)}</strong><em>parts per million</em><time dateTime={co2.latest.observed_at}>Observed {formatClimateDate(co2.latest.observed_at)}</time></div>
          <CO2Chart points={co2.series} />
          <div className="climate-story-footer"><SourceBadge source={co2.source} /><p>This bounded API history shows the period supplied here; it is not presented as the full industrial-era CO₂ record.</p></div><SourcePanel source={co2.source} />
        </> : <DataUnavailable label="Atmospheric CO₂ data" />}</div>
      </StoryReveal>

      <StoryReveal className="climate-story-section climate-temperature-story">
        <SectionLead index="03" eyebrow="Global temperature" title="Difference from a reference climate."><p>A temperature anomaly is the difference between an observed temperature and the average for a stated reference period—not Earth&apos;s absolute temperature.</p></SectionLead>
        <div className="climate-story-content">{temperature?.latest_anomaly && temperature.historical_series.length > 0 ? <>
          <div className="climate-reading-row"><div className="climate-primary-reading"><span>Latest monthly anomaly</span><strong>{formatSigned(temperature.latest_anomaly.value, 3)}°C</strong><em>relative to {temperature.baseline}</em><time dateTime={temperature.latest_anomaly.observed_at}>{temperature.latest_anomaly.period}</time></div><div className="climate-version"><span>Product</span><strong>NOAAGlobalTemp</strong><span>Version {temperature.product_version}</span></div></div>
          <TemperatureChart points={temperature.historical_series} /><SourceBadge source={temperature.source} /><SourcePanel source={temperature.source} />
        </> : <DataUnavailable label="Global temperature data" />}</div>
      </StoryReveal>

      <section className="climate-ocean-field"><StoryReveal className="climate-ocean-inner">
        <SectionLead index="04" eyebrow="Ocean & sea ice" title="The monthly ocean pulse."><p>Issued Copernicus analysis places ocean temperature and polar sea ice in the context of an equivalent month.</p></SectionLead>
        {bulletin && overview ? <div className="climate-ocean-content">
          <article className="climate-ocean-feature"><div className="climate-ocean-rings" aria-hidden="true"><Waves /></div><div><DataTypeBadge type="analysis" /><p>{overview.ocean.reference_period}</p><h3>{overview.ocean.headline}</h3><p>{overview.ocean.summary}</p><SourceBadge source={overview.ocean.source} compact /></div></article>
          <div className="climate-ice-pair">{[{ label: "Arctic", icon: Snowflake, data: overview.sea_ice.arctic }, { label: "Antarctic", icon: Globe2, data: overview.sea_ice.antarctic }].map(({ label, icon: Icon, data }) => <article key={label}><Icon aria-hidden="true" /><p>{label} · {data.reference_period}</p><h3>{data.headline}</h3><p>{data.summary}</p>{data.rank && <strong>Ranked {data.rank}{data.rank_qualifier ? ` ${data.rank_qualifier}` : ""}</strong>}</article>)}</div>
          <MethodologyNote>Sea-ice extent changes strongly with season, so monthly context should compare equivalent times of year.</MethodologyNote><div className="climate-story-footer"><SourceBadge source={bulletin.source} /><p>Bulletin issued {formatClimateDate(bulletin.issue_date)} for {bulletin.reference_period}.</p></div>
        </div> : <DataUnavailable label="Ocean and sea-ice analysis" />}
      </StoryReveal></section>

      <StoryReveal className="climate-story-section climate-enso-story">
        <SectionLead index="05" eyebrow="Pacific climate driver" title="ENSO, separated by evidence type."><p>The observed Niño 3.4 index, an issued expert analysis, and future outlook probabilities answer different questions. This layout keeps them visibly apart.</p></SectionLead>
        <div className="climate-story-content">{enso ? <>
          <div className="enso-evidence-grid">
            <article className="enso-observed"><div><DataTypeBadge type="observation" /><span>Observed</span></div><h3>{enso.observations.latest_nino34 ? `${formatSigned(enso.observations.latest_nino34.value)} °C` : "Unavailable"}</h3><p>{enso.observations.latest_nino34?.period ?? "Latest Niño 3.4 observation unavailable."}</p><DataFreshness freshness={enso.observation_freshness} /></article>
            <article className="enso-analysis"><div><DataTypeBadge type="analysis" /><span>Official analysis</span></div><h3>{enso.status.alert_status}</h3><p>{enso.status.headline}</p><time dateTime={enso.status.issued_at}>Issued {formatClimateDate(enso.status.issued_at)}</time></article>
            <article className="enso-forecast"><div><DataTypeBadge type="forecast" /><span>Issued outlook</span></div><h3>{enso.outlook.wmo.headline}</h3><p>{enso.outlook.wmo.summary}</p>{enso.outlook.wmo.probabilities.map((item) => <p className="enso-probability" key={`${item.label}-${item.valid_period}`}><strong>{formatProbability(item.probability, item.qualifier ?? "not_specified")}</strong>{item.label}<span>{item.valid_period}</span></p>)}</article>
          </div>
          {enso.observations.nino34_series.length > 0 ? <ENSOChart points={enso.observations.nino34_series} /> : <DataUnavailable label="Niño 3.4 trend" />}<div className="climate-story-footer"><SourceBadge source={enso.observations.source} /><p>Warm and cool colors indicate anomaly direction; text labels and the zero-reference line carry the same meaning without relying on color alone.</p></div><SourcePanel source={enso.status.source} title="NOAA analysis source" />
        </> : <DataUnavailable label="ENSO intelligence" />}</div>
      </StoryReveal>

      <section className="climate-forecast-field"><StoryReveal className="climate-forecast-inner">
        <SectionLead index="06" eyebrow="Seasonal outlook · Forecast" title="What should we watch next?"><p>Seasonal outlooks describe shifts in the likelihood of broad conditions over periods such as three months. They are not daily weather forecasts.</p></SectionLead>
        {outlook ? <div className="climate-forecast-content">
          <div className="forecast-header"><div><DataTypeBadge type="forecast" /><span>{humanize(outlook.forecast_period.validity)}</span></div><h3>{outlook.forecast_period.label}</h3><p>Issued {formatClimateDate(outlook.issue.issue_date)} · Baseline {outlook.baseline}</p></div>
          <div className="forecast-drivers">{[outlook.oceanic_drivers.enso, outlook.oceanic_drivers.iod, ...outlook.oceanic_drivers.tropical_atlantic].filter((driver) => driver !== null).map((driver) => <article key={driver.name}><Wind aria-hidden="true" /><p>{driver.name}</p><h4>{humanize(driver.phase)}</h4><p>{driver.status}</p>{driver.forecast_value !== null && <strong>{formatSigned(driver.forecast_value, 1)} {driver.unit}</strong>}<span>{driver.valid_period}</span></article>)}</div>
          <div className="forecast-tendencies">{[{ icon: ThermometerSun, label: "Temperature outlook", data: outlook.temperature }, { icon: CloudRain, label: "Precipitation outlook", data: outlook.precipitation }].map(({ icon: Icon, label, data }) => <article key={label}><Icon aria-hidden="true" /><p>{label}</p><h3>{data.headline}</h3><p>{data.narrative}</p><ul>{data.tendencies.map((item) => <li key={`${item.region}-${item.category}`}><span>{humanize(item.category)}</span><strong>{formatProbability(item.probability, item.qualifier)}</strong><small>{item.region}</small></li>)}</ul></article>)}</div>
          <div className="what-to-watch"><p>What to Watch</p><ol>{outlook.key_messages.map((message, index) => <li key={message}><span>0{index + 1}</span><p>{message}<small>{outlook.forecast_period.label} · WMO · issued {formatClimateDate(outlook.issue.issue_date)}</small></p></li>)}</ol></div>
          <div className="tercile-explainer"><Gauge aria-hidden="true" /><div><h3>Reading seasonal terciles</h3><p>{outlook.methodology.tercile_explanation}</p><p>{outlook.methodology.driver_interaction_note}</p></div></div><SourceBadge source={outlook.sources[0]} /><SourcePanel source={outlook.sources[0]} title="WMO outlook method" />
        </div> : <DataUnavailable label="Seasonal outlook" detail="No verified WMO outlook could be reached; observed climate sections remain available." />}
      </StoryReveal></section>

      <StoryReveal className="climate-events-section">
        <SectionLead index="07" eyebrow="Current Earth events" title="Signals from a restless planet."><p>A bounded recent selection from NASA EONET. Event detection supplies location and source context; it does not establish climate causation.</p></SectionLead>
        {events ? <>
          {events.events.length > 0 ? <ol className="earth-event-track">{events.events.map((event, index) => { const eventDate = event.latest_geometry?.date ?? event.closed_at; const coordinates = event.latest_geometry ? coordinatesLabel(event.latest_geometry.coordinates) : null; const eventSource = event.sources[0]?.url ?? event.eonet_url; return <li key={event.id}><div><span>{String(index + 1).padStart(2, "0")}</span><Activity aria-hidden="true" /></div><p>{event.categories.map((category) => category.title).join(" · ") || "Earth event"}</p><h3>{event.title}</h3>{eventDate && <time dateTime={eventDate}><CalendarDays size={14} aria-hidden="true" />{formatClimateDate(eventDate)}</time>}{coordinates && <p className="event-coordinates">{coordinates}</p>}{eventSource && <a href={eventSource} target="_blank" rel="noreferrer">Original event source <ArrowUpRight size={14} aria-hidden="true" /></a>}</li>; })}</ol> : <DataUnavailable label="Recent Earth event list" detail="NASA EONET returned no events for this bounded query." />}
          <div className="event-disclaimer"><Globe2 aria-hidden="true" /><p>{events.attribution_disclaimer}</p></div><div className="climate-story-footer"><SourceBadge source={events.source} /><p>Showing up to 8 events from the last 30 days. The full map belongs to a later Earth Events experience.</p></div>
        </> : <DataUnavailable label="NASA Earth Events" />}
      </StoryReveal>

      <footer className="climate-now-footer"><div><p>EcoPulse climate intelligence</p><strong>Every signal should reveal its source, date, and evidence type.</strong></div><nav aria-label="Climate Now footer"><Link href="/sources">Sources &amp; methodology</Link><Link href="/outlooks">Outlooks</Link><Link href="/events">Earth Events</Link></nav></footer>
    </main>
  );
}
