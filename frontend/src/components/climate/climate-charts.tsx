"use client";

import { useReducedMotion } from "framer-motion";
import { Area, AreaChart, CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { formatClimateDate, formatSigned } from "@/lib/climate-format";
import type { ClimateSeriesPoint, ENSOObservation, TemperaturePoint } from "@/types/climate";

const tooltipStyle = {
  background: "var(--surface)",
  border: "1px solid var(--border-strong)",
  borderRadius: "0.65rem",
  color: "var(--foreground)",
  fontSize: "0.75rem",
};

function ChartFrame({ label, summary, children }: { label: string; summary: string; children: React.ReactNode }) {
  return (
    <figure className="climate-chart" role="img" aria-label={label}>
      <div aria-hidden="true" className="climate-chart-canvas">{children}</div>
      <figcaption>{summary}</figcaption>
    </figure>
  );
}

export function CO2Chart({ points }: { points: ClimateSeriesPoint[] }) {
  const reduceMotion = useReducedMotion();
  const data = points.map((point) => ({ date: point.observed_at, value: point.value }));
  const first = data[0];
  const last = data.at(-1);
  const summary = first && last ? `The displayed NOAA series runs from ${formatClimateDate(first.date)} at ${first.value.toFixed(2)} ppm to ${formatClimateDate(last.date)} at ${last.value.toFixed(2)} ppm.` : "No CO₂ series is available.";
  return (
    <ChartFrame label="Recent atmospheric carbon dioxide concentration line chart" summary={summary}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 12, right: 8, bottom: 4, left: -12 }}>
          <defs><linearGradient id="co2-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--primary)" stopOpacity={0.34} /><stop offset="100%" stopColor="var(--primary)" stopOpacity={0} /></linearGradient></defs>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis dataKey="date" tickFormatter={(value: string) => formatClimateDate(value, { month: "short", day: "numeric", timeZone: "UTC" })} minTickGap={48} tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={["dataMin - 0.5", "dataMax + 0.5"]} tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} width={54} unit=" ppm" />
          <Tooltip contentStyle={tooltipStyle} labelFormatter={(value) => formatClimateDate(String(value))} formatter={(value) => [`${Number(value).toFixed(2)} ppm`, "Atmospheric CO₂"]} />
          <Area dataKey="value" type="monotone" stroke="var(--primary)" strokeWidth={2.5} fill="url(#co2-fill)" isAnimationActive={!reduceMotion} activeDot={{ r: 6, fill: "var(--primary)" }} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function ENSOChart({ points }: { points: ENSOObservation[] }) {
  const reduceMotion = useReducedMotion();
  const data = points.map((point) => ({ date: point.observed_at, value: point.value }));
  const latest = data.at(-1);
  return (
    <ChartFrame label="Recent weekly Niño 3.4 sea-surface temperature anomaly line chart" summary={latest ? `The latest plotted Niño 3.4 observation is ${formatSigned(latest.value)} °C anomaly on ${formatClimateDate(latest.date)}. The zero line marks the reference-period average.` : "No Niño 3.4 observations are available."}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 8, bottom: 4, left: -12 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis dataKey="date" tickFormatter={(value: string) => formatClimateDate(value, { month: "short", day: "numeric", timeZone: "UTC" })} minTickGap={45} tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} width={48} unit="°" />
          <ReferenceLine y={0} stroke="var(--data-trend)" strokeDasharray="4 4" label={{ value: "0°C reference", position: "insideTopLeft", fill: "var(--muted)", fontSize: 10 }} />
          <Tooltip contentStyle={tooltipStyle} labelFormatter={(value) => formatClimateDate(String(value))} formatter={(value) => [`${formatSigned(Number(value))} °C`, "Niño 3.4 anomaly"]} />
          <Line dataKey="value" type="monotone" stroke="var(--data-warm-strong)" strokeWidth={2.5} dot={false} isAnimationActive={!reduceMotion} activeDot={{ r: 6, fill: "var(--data-warm-strong)" }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}

export function TemperatureChart({ points }: { points: TemperaturePoint[] }) {
  const reduceMotion = useReducedMotion();
  const data = points.map((point) => ({ date: point.observed_at, period: point.period, value: point.value }));
  const latest = data.at(-1);
  return (
    <ChartFrame label="Recent monthly global surface temperature anomaly area chart" summary={latest ? `The latest plotted monthly anomaly is ${formatSigned(latest.value, 3)} °C for ${latest.period}, relative to the stated climate baseline.` : "No monthly temperature series is available."}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 12, right: 8, bottom: 4, left: -12 }}>
          <defs><linearGradient id="temperature-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--heat)" stopOpacity={0.36} /><stop offset="100%" stopColor="var(--heat)" stopOpacity={0.02} /></linearGradient></defs>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis dataKey="date" tickFormatter={(value: string) => formatClimateDate(value, { month: "short", year: "2-digit", timeZone: "UTC" })} minTickGap={46} tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} width={48} unit="°" />
          <ReferenceLine y={0} stroke="var(--data-trend)" strokeDasharray="4 4" />
          <Tooltip contentStyle={tooltipStyle} labelFormatter={(_, payload) => payload?.[0]?.payload?.period ?? "Monthly anomaly"} formatter={(value) => [`${formatSigned(Number(value), 3)} °C`, "Temperature anomaly"]} />
          <Area dataKey="value" type="monotone" stroke="var(--heat)" strokeWidth={2.5} fill="url(#temperature-fill)" isAnimationActive={!reduceMotion} activeDot={{ r: 6, fill: "var(--heat)" }} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartFrame>
  );
}
