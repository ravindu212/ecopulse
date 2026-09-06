import { BookOpenText, CircleAlert, ExternalLink } from "lucide-react";

import { formatClimateDate, humanize } from "@/lib/climate-format";
import type { ClimateDataType, ClimateFreshness, SourceMetadata } from "@/types/climate";

export function DataTypeBadge({ type }: { type: ClimateDataType }) {
  return <span className={`climate-type climate-type-${type}`}>{humanize(type)}</span>;
}

export function DataFreshness({ freshness, issued = false }: { freshness: ClimateFreshness; issued?: boolean }) {
  const label = issued && freshness === "current" ? "Latest issued analysis" : humanize(freshness);
  return <span className={`climate-freshness climate-freshness-${freshness}`}><span aria-hidden="true" />{label}</span>;
}

export function SourceBadge({ source, compact = false }: { source: SourceMetadata; compact?: boolean }) {
  const temporalDate = source.observed_at ?? source.published_at ?? source.fetched_at;
  const temporalLabel = source.observed_at
    ? "Observed"
    : source.published_at
      ? "Issued"
      : "Fetched";
  return (
    <div className={`climate-source-badge ${compact ? "climate-source-badge-compact" : ""}`}>
      <div className="climate-source-badge-top">
        <DataTypeBadge type={source.data_type} />
        <DataFreshness freshness={source.freshness} issued={source.data_type === "analysis"} />
      </div>
      <a href={source.source_url} target="_blank" rel="noreferrer">
        <span>{source.publisher}</span><ExternalLink size={13} aria-hidden="true" />
      </a>
      {temporalDate && (
        <time dateTime={temporalDate}>
          {temporalLabel} {formatClimateDate(temporalDate)}
        </time>
      )}
    </div>
  );
}

export function SourcePanel({ source, title = "Source & method" }: { source: SourceMetadata; title?: string }) {
  return (
    <details className="climate-source-panel">
      <summary><BookOpenText size={16} aria-hidden="true" />{title}</summary>
      <div>
        <SourceBadge source={source} />
        {source.baseline && <p><strong>Reference:</strong> {source.baseline}</p>}
        {source.methodology_note && <p>{source.methodology_note}</p>}
      </div>
    </details>
  );
}

export function MethodologyNote({ children }: { children: React.ReactNode }) {
  return <p className="climate-methodology"><BookOpenText size={16} aria-hidden="true" />{children}</p>;
}

export function DataUnavailable({ label, detail }: { label: string; detail?: string }) {
  return (
    <div className="climate-unavailable" role="status">
      <CircleAlert size={21} aria-hidden="true" />
      <div><strong>{label} is temporarily unavailable.</strong><p>{detail ?? "Other verified climate signals remain available."}</p></div>
    </div>
  );
}
