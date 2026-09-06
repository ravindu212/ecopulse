export type ClimateDataType = "observation" | "analysis" | "forecast" | "model" | "estimate";
export type ClimateFreshness = "live" | "current" | "stale" | "unavailable";
export type ProbabilityQualifier = "exact" | "greater_than" | "less_than" | "near" | "range" | "not_specified";
export type SeasonalValidity = "upcoming" | "current" | "expired";
export type SeasonalCategory = "above_normal" | "near_normal" | "below_normal" | "equal_chances" | "unknown";

export type SourceMetadata = {
  source_name: string;
  source_url: string;
  publisher: string;
  data_type: ClimateDataType;
  observed_at: string | null;
  published_at: string | null;
  fetched_at: string | null;
  freshness: ClimateFreshness;
  methodology_note: string | null;
  baseline: string | null;
};

export type ClimateSeriesPoint = {
  value: number;
  unit: string;
  observed_at: string;
};

export type ClimateNumericDatum = ClimateSeriesPoint & {
  label: string;
  source: SourceMetadata;
  methodology_note: string | null;
};

export type ClimateCO2 = {
  latest: ClimateNumericDatum | null;
  series: ClimateSeriesPoint[];
  source: SourceMetadata;
  status: ClimateFreshness;
};

export type ENSOPhase = "el_nino" | "la_nina" | "neutral" | "unknown";

export type ENSOObservation = {
  region: "nino_1_2" | "nino_3" | "nino_3_4" | "nino_4";
  region_name: string;
  value: number;
  unit: string;
  period: string;
  observed_at: string;
  source: SourceMetadata;
  methodology_note: string;
};

export type ENSOProbability = {
  label: string;
  probability: number | null;
  unit: string;
  qualifier: ProbabilityQualifier | null;
  valid_period: string;
  issued_at: string;
  source: SourceMetadata;
};

export type ENSOIssuedOutlook = {
  publisher: string;
  issue_date: string;
  verified_at: string;
  headline: string;
  summary: string;
  probabilities: ENSOProbability[];
  valid_period: string | null;
  source: SourceMetadata;
  latest_known_issue: boolean;
  methodology_note: string;
};

export type ClimateENSO = {
  status: {
    alert_status: string;
    enso_phase: ENSOPhase;
    headline: string;
    summary: string;
    issued_at: string;
    source: SourceMetadata;
    latest_known_issue: boolean;
  };
  observations: {
    latest_nino34: ENSOObservation | null;
    regions: ENSOObservation[];
    nino34_series: ENSOObservation[];
    source: SourceMetadata;
    freshness: ClimateFreshness;
  };
  outlook: { noaa: ENSOIssuedOutlook; wmo: ENSOIssuedOutlook };
  sources: SourceMetadata[];
  observation_freshness: ClimateFreshness;
  explanatory_notes: string[];
};

export type TemperaturePoint = {
  value: number;
  unit: string;
  period: string;
  observed_at: string;
};

export type GlobalTemperature = {
  latest_anomaly: (TemperaturePoint & { label: string; source: SourceMetadata; methodology_note: string }) | null;
  historical_series: TemperaturePoint[];
  baseline: string;
  product_version: string;
  source: SourceMetadata;
  methodology_note: string;
  freshness: ClimateFreshness;
};

export type IssuedClimateContext = {
  indicator: string;
  headline: string;
  summary: string;
  reference_period: string;
  rank: number | null;
  rank_qualifier: string | null;
  source: SourceMetadata;
};

export type ClimateBulletin = {
  publisher: string;
  issue_date: string;
  reference_period: string;
  verified_at: string;
  source_url: string;
  temperature_context: IssuedClimateContext;
  sea_surface_temperature_context: IssuedClimateContext;
  arctic_sea_ice_context: IssuedClimateContext;
  antarctic_sea_ice_context: IssuedClimateContext;
  precipitation_extremes_note: string | null;
  source: SourceMetadata;
  latest_known_issue: boolean;
  methodology_note: string;
};

export type ClimateOverview = {
  generated_at: string;
  co2: { latest: ClimateNumericDatum | null; freshness: ClimateFreshness; source: SourceMetadata };
  enso: {
    status: ClimateENSO["status"];
    latest_nino34: ENSOObservation | null;
    observation_freshness: ClimateFreshness;
    observation_source: SourceMetadata;
  };
  global_temperature: GlobalTemperature;
  ocean: IssuedClimateContext;
  sea_ice: { arctic: IssuedClimateContext; antarctic: IssuedClimateContext };
  earth_events: {
    returned_event_count: number;
    window_days: number;
    result_limit: number;
    freshness: ClimateFreshness;
    source: SourceMetadata;
    attribution_disclaimer: string;
  };
  latest_bulletin: ClimateBulletin;
  seasonal_outlook: {
    period: string;
    headline: string;
    issue_date: string;
    key_driver_summary: string;
    validity: SeasonalValidity;
  } | null;
  sources: SourceMetadata[];
  availability: {
    available_components: string[];
    stale_components: string[];
    unavailable_components: string[];
  };
};

export type SeasonalOceanDriver = {
  name: string;
  phase: string;
  status: string;
  forecast_value: number | null;
  unit: string | null;
  valid_period: string;
  confidence: string | null;
  source: SourceMetadata;
  methodology_note: string;
};

export type SeasonalProbability = {
  category: SeasonalCategory;
  probability: number | null;
  unit: string;
  qualifier: ProbabilityQualifier;
  valid_period: string;
  region: string;
  source: SourceMetadata;
};

export type SeasonalOutlookSection = {
  headline: string;
  narrative: string;
  forecast_period: string;
  baseline: string;
  probabilistic: boolean;
  tendencies: SeasonalProbability[];
  source: SourceMetadata;
};

export type ClimateOutlook = {
  issue: {
    publisher: string;
    issue_date: string;
    verified_at: string;
    source_url: string;
    data_type: "forecast";
    latest_known_issue: boolean;
  };
  forecast_period: {
    label: string;
    start_date: string;
    end_date: string;
    validity: SeasonalValidity;
  };
  baseline: string;
  oceanic_drivers: {
    enso: SeasonalOceanDriver;
    iod: SeasonalOceanDriver | null;
    tropical_atlantic: SeasonalOceanDriver[];
  };
  temperature: SeasonalOutlookSection;
  precipitation: SeasonalOutlookSection;
  key_messages: string[];
  methodology: {
    multi_model_method: string;
    outlook_meaning: string;
    tercile_explanation: string;
    driver_interaction_note: string;
  };
  limitations: string[];
  sources: SourceMetadata[];
};

export type EarthEvent = {
  id: string;
  title: string;
  description: string | null;
  categories: { id: string; title: string }[];
  status: string;
  closed_at: string | null;
  latest_geometry: { date: string; type: string; coordinates: unknown[] } | null;
  magnitude: { value: number; unit: string | null; description: string | null } | null;
  sources: { id: string | null; title: string | null; url: string }[];
  eonet_url: string | null;
  source: SourceMetadata;
};

export type EarthEvents = {
  events: EarthEvent[];
  count: number;
  source: SourceMetadata;
  fetched_at: string;
  freshness: ClimateFreshness;
  attribution_disclaimer: string;
};
