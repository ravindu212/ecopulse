import logging
import math
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings
from app.schemas.climate import (
    ClimateFreshness,
    EarthEvent,
    EarthEventCategory,
    EarthEventGeometry,
    EarthEventMagnitude,
    EarthEventSource,
    EarthEventsResponse,
    SourceMetadata,
)
from app.services.climate.cache import TTLCache, utc_now
from app.services.climate.co2_service import ClimateDataParseError
from app.services.climate.http_client import ProviderHttpClient, ProviderRequestError
from app.services.climate.source_registry import EARTH_EVENT_ATTRIBUTION_DISCLAIMER, eonet_source


logger = logging.getLogger(__name__)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _normalise_event(raw: Any, source: SourceMetadata) -> EarthEvent | None:
    if not isinstance(raw, dict) or not raw.get("id") or not raw.get("title"):
        return None

    categories = []
    for category in raw.get("categories") or []:
        if (
            isinstance(category, dict)
            and category.get("id") is not None
            and category.get("title")
        ):
            categories.append(
                EarthEventCategory(id=str(category["id"]), title=str(category["title"]))
            )

    sources = []
    for event_source in raw.get("sources") or []:
        if isinstance(event_source, dict) and event_source.get("url"):
            sources.append(
                EarthEventSource(
                    id=str(event_source["id"])
                    if event_source.get("id") is not None
                    else None,
                    title=str(event_source["title"]) if event_source.get("title") else None,
                    url=str(event_source["url"]),
                )
            )

    geometries: list[tuple[datetime, dict[str, Any]]] = []
    for geometry in raw.get("geometry") or []:
        if not isinstance(geometry, dict):
            continue
        date = _parse_datetime(geometry.get("date"))
        coordinates = geometry.get("coordinates")
        geometry_type = geometry.get("type")
        if (
            date is not None
            and isinstance(geometry_type, str)
            and isinstance(coordinates, list)
        ):
            geometries.append((date, geometry))

    latest_geometry = None
    magnitude = None
    if geometries:
        geometry_date, geometry = max(geometries, key=lambda item: item[0])
        latest_geometry = EarthEventGeometry(
            date=geometry_date,
            type=geometry["type"],
            coordinates=geometry["coordinates"],
        )
        magnitude_value = geometry.get("magnitudeValue")
        if magnitude_value is not None:
            try:
                numeric_magnitude = float(magnitude_value)
                if math.isfinite(numeric_magnitude):
                    magnitude = EarthEventMagnitude(
                        value=numeric_magnitude,
                        unit=str(geometry["magnitudeUnit"])
                        if geometry.get("magnitudeUnit")
                        else None,
                        description=str(geometry["magnitudeDescription"])
                        if geometry.get("magnitudeDescription")
                        else None,
                    )
            except (TypeError, ValueError):
                pass

    closed_at = _parse_datetime(raw.get("closed"))
    return EarthEvent(
        id=str(raw["id"]),
        title=str(raw["title"]),
        description=str(raw["description"]) if raw.get("description") else None,
        categories=categories,
        status="closed" if closed_at is not None else "open",
        closed_at=closed_at,
        latest_geometry=latest_geometry,
        magnitude=magnitude,
        sources=sources,
        eonet_url=str(raw["link"]) if raw.get("link") else None,
        source=source,
    )


def parse_eonet_events(payload: Any, source: SourceMetadata, limit: int) -> list[EarthEvent]:
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ClimateDataParseError("EONET response shape was not recognized")
    events = [event for raw in payload["events"] if (event := _normalise_event(raw, source))]
    minimum = datetime.min.replace(tzinfo=timezone.utc)
    events.sort(
        key=lambda event: (
            event.latest_geometry.date if event.latest_geometry else minimum,
            event.title.casefold(),
            event.id,
        ),
        reverse=True,
    )
    return events[:limit]


class EarthEventsService:
    def __init__(
        self,
        http_client: ProviderHttpClient | None = None,
        cache: TTLCache[EarthEventsResponse] | None = None,
        source_url: str = settings.climate_eonet_url,
        ttl_seconds: int = settings.climate_events_ttl_seconds,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._http = http_client or ProviderHttpClient()
        self._cache = cache or TTLCache(clock=clock)
        self._source_url = source_url
        self._ttl_seconds = ttl_seconds
        self._clock = clock

    def get_events(
        self,
        category: str | None = None,
        days: int = 30,
        limit: int = 20,
    ) -> EarthEventsResponse:
        cache_key = f"eonet:{category or '*'}:{days}:{limit}"
        cached = self._cache.get_fresh(cache_key)
        if cached is not None:
            return cached.value

        try:
            params: dict[str, str | int] = {"status": "open", "days": days, "limit": limit}
            if category:
                params["category"] = category
            payload = self._http.get_json(self._source_url, params=params)
            fetched_at = self._clock()
            source = eonet_source(self._source_url, ClimateFreshness.current, fetched_at)
            events = parse_eonet_events(payload, source, limit)
            response = EarthEventsResponse(
                events=events,
                count=len(events),
                source=source,
                fetched_at=fetched_at,
                freshness=ClimateFreshness.current,
                attribution_disclaimer=EARTH_EVENT_ATTRIBUTION_DISCLAIMER,
            )
            self._cache.put(cache_key, response, self._ttl_seconds)
            return response
        except (ProviderRequestError, ClimateDataParseError, TypeError, ValueError) as exc:
            logger.warning("NASA EONET refresh failed: %s", type(exc).__name__)
            stale = self._cache.get_last_known_good(cache_key)
            if stale is not None:
                return self._as_stale(stale.value)
            fetched_at = self._clock()
            source = eonet_source(self._source_url, ClimateFreshness.unavailable, fetched_at)
            return EarthEventsResponse(
                events=[],
                count=0,
                source=source,
                fetched_at=fetched_at,
                freshness=ClimateFreshness.unavailable,
                attribution_disclaimer=EARTH_EVENT_ATTRIBUTION_DISCLAIMER,
            )

    @staticmethod
    def _as_stale(response: EarthEventsResponse) -> EarthEventsResponse:
        source = response.source.model_copy(update={"freshness": ClimateFreshness.stale})
        events = [
            event.model_copy(
                update={
                    "source": event.source.model_copy(
                        update={"freshness": ClimateFreshness.stale}
                    )
                }
            )
            for event in response.events
        ]
        return response.model_copy(
            update={
                "events": events,
                "source": source,
                "freshness": ClimateFreshness.stale,
            }
        )
