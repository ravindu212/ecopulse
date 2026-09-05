from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ClimateDataType(str, Enum):
    observation = "observation"
    analysis = "analysis"
    forecast = "forecast"
    model = "model"
    estimate = "estimate"


class ClimateFreshness(str, Enum):
    live = "live"
    current = "current"
    stale = "stale"
    unavailable = "unavailable"


class ENSOPhase(str, Enum):
    el_nino = "el_nino"
    la_nina = "la_nina"
    neutral = "neutral"
    unknown = "unknown"


class ENSORegion(str, Enum):
    nino_1_2 = "nino_1_2"
    nino_3 = "nino_3"
    nino_3_4 = "nino_3_4"
    nino_4 = "nino_4"


class ProbabilityQualifier(str, Enum):
    exact = "exact"
    greater_than = "greater_than"
    less_than = "less_than"
    near = "near"
    range = "range"
    not_specified = "not_specified"


class SeasonalOutlookValidity(str, Enum):
    upcoming = "upcoming"
    current = "current"
    expired = "expired"


class SeasonalDriverPhase(str, Enum):
    el_nino = "el_nino"
    la_nina = "la_nina"
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    above_normal = "above_normal"
    below_normal = "below_normal"
    unknown = "unknown"


class SeasonalTercileCategory(str, Enum):
    above_normal = "above_normal"
    near_normal = "near_normal"
    below_normal = "below_normal"
    equal_chances = "equal_chances"
    unknown = "unknown"


class SourceMetadata(BaseModel):
    source_name: str
    source_url: str
    publisher: str
    data_type: ClimateDataType
    observed_at: datetime | None = None
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    freshness: ClimateFreshness
    methodology_note: str | None = None
    baseline: str | None = None


class ClimateNumericDatum(BaseModel):
    label: str
    value: float
    unit: str
    observed_at: datetime
    source: SourceMetadata
    methodology_note: str | None = None


class ClimateSeriesPoint(BaseModel):
    value: float
    unit: str
    observed_at: datetime


class CO2Response(BaseModel):
    latest: ClimateNumericDatum | None
    series: list[ClimateSeriesPoint]
    source: SourceMetadata
    status: ClimateFreshness


class EarthEventCategory(BaseModel):
    id: str
    title: str


class EarthEventSource(BaseModel):
    id: str | None = None
    title: str | None = None
    url: str


class EarthEventGeometry(BaseModel):
    date: datetime
    type: str
    coordinates: list[Any]


class EarthEventMagnitude(BaseModel):
    value: float
    unit: str | None = None
    description: str | None = None


class EarthEvent(BaseModel):
    id: str
    title: str
    description: str | None = None
    categories: list[EarthEventCategory]
    status: str
    closed_at: datetime | None = None
    latest_geometry: EarthEventGeometry | None = None
    magnitude: EarthEventMagnitude | None = None
    sources: list[EarthEventSource]
    eonet_url: str | None = None
    source: SourceMetadata


class EarthEventsResponse(BaseModel):
    events: list[EarthEvent]
    count: int = Field(ge=0)
    source: SourceMetadata
    fetched_at: datetime
    freshness: ClimateFreshness
    attribution_disclaimer: str


class ENSOObservation(BaseModel):
    region: ENSORegion
    region_name: str
    value: float
    unit: str
    period: str
    observed_at: datetime
    source: SourceMetadata
    methodology_note: str


class ENSOObservations(BaseModel):
    latest_nino34: ENSOObservation | None
    regions: list[ENSOObservation]
    nino34_series: list[ENSOObservation]
    source: SourceMetadata
    freshness: ClimateFreshness


class ENSOStatus(BaseModel):
    alert_status: str
    enso_phase: ENSOPhase
    headline: str
    summary: str
    issued_at: date
    source: SourceMetadata
    latest_known_issue: bool


class ENSOProbability(BaseModel):
    label: str
    probability: float | None = Field(default=None, ge=0, le=100)
    unit: str = "percent"
    qualifier: ProbabilityQualifier | None = None
    valid_period: str
    issued_at: date
    source: SourceMetadata


class ENSOIssuedOutlook(BaseModel):
    publisher: str
    issue_date: date
    verified_at: date
    headline: str
    summary: str
    probabilities: list[ENSOProbability]
    valid_period: str | None = None
    source: SourceMetadata
    latest_known_issue: bool
    methodology_note: str


class ENSOOutlook(BaseModel):
    noaa: ENSOIssuedOutlook
    wmo: ENSOIssuedOutlook


class ENSOResponse(BaseModel):
    status: ENSOStatus
    observations: ENSOObservations
    outlook: ENSOOutlook
    sources: list[SourceMetadata]
    observation_freshness: ClimateFreshness
    explanatory_notes: list[str]


class TemperatureAnomalyPoint(BaseModel):
    value: float
    unit: str
    period: str
    observed_at: datetime


class TemperatureAnomaly(TemperatureAnomalyPoint):
    label: str
    source: SourceMetadata
    methodology_note: str


class GlobalTemperatureResponse(BaseModel):
    latest_anomaly: TemperatureAnomaly | None
    historical_series: list[TemperatureAnomalyPoint]
    baseline: str
    product_version: str
    source: SourceMetadata
    methodology_note: str
    freshness: ClimateFreshness


class IssuedClimateContext(BaseModel):
    indicator: str
    headline: str
    summary: str
    reference_period: str
    rank: int | None = Field(default=None, ge=1)
    rank_qualifier: str | None = None
    source: SourceMetadata


class ClimateBulletin(BaseModel):
    publisher: str
    issue_date: date
    reference_period: str
    verified_at: date
    source_url: str
    temperature_context: IssuedClimateContext
    sea_surface_temperature_context: IssuedClimateContext
    arctic_sea_ice_context: IssuedClimateContext
    antarctic_sea_ice_context: IssuedClimateContext
    precipitation_extremes_note: str | None = None
    source: SourceMetadata
    latest_known_issue: bool
    methodology_note: str


class ForecastPeriod(BaseModel):
    label: str
    start_date: date
    end_date: date
    validity: SeasonalOutlookValidity


class SeasonalProbability(BaseModel):
    category: SeasonalTercileCategory
    probability: float | None = Field(default=None, ge=0, le=100)
    unit: str = "percent"
    qualifier: ProbabilityQualifier = ProbabilityQualifier.not_specified
    valid_period: str
    region: str
    source: SourceMetadata


class SeasonalOceanDriver(BaseModel):
    name: str
    phase: SeasonalDriverPhase
    status: str
    forecast_value: float | None = None
    unit: str | None = None
    valid_period: str
    confidence: str | None = None
    source: SourceMetadata
    methodology_note: str


class SeasonalOceanicDrivers(BaseModel):
    enso: SeasonalOceanDriver
    iod: SeasonalOceanDriver | None = None
    tropical_atlantic: list[SeasonalOceanDriver]


class SeasonalOutlookSection(BaseModel):
    headline: str
    narrative: str
    forecast_period: str
    baseline: str
    probabilistic: bool = True
    tendencies: list[SeasonalProbability]
    source: SourceMetadata


class SeasonalOutlookIssue(BaseModel):
    publisher: str
    issue_date: date
    verified_at: date
    source_url: str
    data_type: ClimateDataType
    latest_known_issue: bool


class SeasonalOutlookMethodology(BaseModel):
    multi_model_method: str
    outlook_meaning: str
    tercile_explanation: str
    driver_interaction_note: str


class SeasonalOutlookResponse(BaseModel):
    issue: SeasonalOutlookIssue
    forecast_period: ForecastPeriod
    baseline: str
    oceanic_drivers: SeasonalOceanicDrivers
    temperature: SeasonalOutlookSection
    precipitation: SeasonalOutlookSection
    key_messages: list[str]
    methodology: SeasonalOutlookMethodology
    limitations: list[str]
    sources: list[SourceMetadata]


class SeasonalOutlookPreview(BaseModel):
    period: str
    headline: str
    issue_date: date
    key_driver_summary: str
    validity: SeasonalOutlookValidity


class CO2Overview(BaseModel):
    latest: ClimateNumericDatum | None
    freshness: ClimateFreshness
    source: SourceMetadata


class ENSOOverview(BaseModel):
    status: ENSOStatus
    latest_nino34: ENSOObservation | None
    observation_freshness: ClimateFreshness
    observation_source: SourceMetadata


class EarthEventsOverview(BaseModel):
    returned_event_count: int = Field(ge=0)
    window_days: int = Field(ge=1)
    result_limit: int = Field(ge=1)
    freshness: ClimateFreshness
    source: SourceMetadata
    attribution_disclaimer: str


class SeaIceOverview(BaseModel):
    arctic: IssuedClimateContext
    antarctic: IssuedClimateContext


class ClimateAvailability(BaseModel):
    available_components: list[str]
    stale_components: list[str]
    unavailable_components: list[str]


class ClimateOverviewResponse(BaseModel):
    generated_at: datetime
    co2: CO2Overview
    enso: ENSOOverview
    global_temperature: GlobalTemperatureResponse
    ocean: IssuedClimateContext
    sea_ice: SeaIceOverview
    earth_events: EarthEventsOverview
    latest_bulletin: ClimateBulletin
    seasonal_outlook: SeasonalOutlookPreview | None
    sources: list[SourceMetadata]
    availability: ClimateAvailability
