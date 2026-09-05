from datetime import datetime
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
