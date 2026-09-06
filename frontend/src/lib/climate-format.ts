export function formatClimateDate(value: string | null | undefined, options?: Intl.DateTimeFormatOptions) {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en", options ?? { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(date);
}

export function formatSigned(value: number, digits = 2) {
  return `${value > 0 ? "+" : ""}${value.toFixed(digits)}`;
}

export function humanize(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function formatProbability(probability: number | null, qualifier: string) {
  if (probability === null) return "Probability not numerically specified";
  const symbols: Record<string, string> = { greater_than: ">", less_than: "<", near: "≈" };
  return `${symbols[qualifier] ?? ""}${probability}%`;
}
