import type { CSSProperties } from "react";

type PlotPoint = { value: number; observed_at: string };

function toPolyline(points: PlotPoint[]) {
  if (points.length === 0) return "";
  const values = points.map((point) => point.value);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const range = maximum - minimum || 1;

  return points
    .map((point, index) => {
      const x = points.length === 1 ? 50 : (index / (points.length - 1)) * 100;
      const y = 88 - ((point.value - minimum) / range) * 68;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

export function SeriesPlot({
  points,
  label,
  summary,
  tone = "cool",
}: {
  points: PlotPoint[];
  label: string;
  summary: string;
  tone?: "cool" | "warm" | "carbon";
}) {
  const polyline = toPolyline(points);

  return (
    <figure className={`home-series home-series-${tone}`} role="img" aria-label={label}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <line x1="0" y1="88" x2="100" y2="88" className="home-series-axis" />
        <line x1="0" y1="54" x2="100" y2="54" className="home-series-grid" />
        {polyline ? (
          <polyline
            points={polyline}
            pathLength="1"
            vectorEffect="non-scaling-stroke"
            style={{ "--series-length": 1 } as CSSProperties}
          />
        ) : null}
      </svg>
      <figcaption>{summary}</figcaption>
    </figure>
  );
}
