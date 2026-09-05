from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.schemas.climate import ClimateFreshness
from app.services.climate.cache import TTLCache
from app.services.climate.events_service import EarthEventsService
from app.services.climate.http_client import ProviderHttpClient


EONET_PAYLOAD = {
    "events": [
        {
            "id": "EONET_1",
            "title": "Open wildfire",
            "description": None,
            "link": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_1",
            "closed": None,
            "categories": [
                {"id": "wildfires", "title": "Wildfires"},
                {"id": "smoke", "title": "Smoke"},
            ],
            "sources": [{"id": "Source A", "url": "https://source.test/a"}],
            "geometry": [
                {
                    "date": "2026-09-01T00:00:00Z",
                    "type": "Point",
                    "coordinates": [80.1, 7.2],
                },
                {
                    "date": "2026-09-04T12:00:00Z",
                    "type": "Point",
                    "coordinates": [81.5, 8.25],
                    "magnitudeValue": 1200,
                    "magnitudeUnit": "acres",
                    "magnitudeDescription": "Affected area",
                },
            ],
        },
        {
            "id": "EONET_2",
            "title": "Closed storm",
            "description": "Archived by the source.",
            "closed": "2026-09-03T00:00:00Z",
            "categories": [{"id": "severeStorms", "title": "Severe Storms"}],
            "sources": [{"id": "Source B", "url": "https://source.test/b"}],
            "geometry": [
                {
                    "date": "2026-09-03T00:00:00Z",
                    "type": "Polygon",
                    "coordinates": [[[79.0, 6.0], [80.0, 7.0], [79.0, 6.0]]],
                }
            ],
        },
    ]
}


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 5, 10, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def make_client(handler):
    return ProviderHttpClient(client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_eonet_normalises_events_preserves_links_geometry_and_magnitude():
    captured_params = {}

    def handler(request):
        captured_params.update(dict(request.url.params))
        return httpx.Response(200, json=EONET_PAYLOAD)

    result = EarthEventsService(http_client=make_client(handler)).get_events(
        category="wildfires", days=14, limit=10
    )

    assert captured_params == {
        "status": "open",
        "days": "14",
        "limit": "10",
        "category": "wildfires",
    }
    assert result.count == 2
    assert result.events[0].id == "EONET_1"
    assert [category.title for category in result.events[0].categories] == ["Wildfires", "Smoke"]
    assert result.events[0].description is None
    assert result.events[0].status == "open"
    assert result.events[1].status == "closed"
    assert result.events[0].sources[0].url == "https://source.test/a"
    assert result.events[0].eonet_url.endswith("EONET_1")
    assert result.events[0].latest_geometry.type == "Point"
    assert result.events[0].latest_geometry.coordinates == [81.5, 8.25]
    assert result.events[1].latest_geometry.type == "Polygon"
    assert result.events[1].latest_geometry.coordinates[0][0] == [79.0, 6.0]
    assert result.events[0].magnitude.value == 1200
    assert result.events[0].magnitude.unit == "acres"
    assert result.events[1].magnitude is None
    assert result.source.publisher == "NASA Earth Science Data Systems"


def test_eonet_selects_newest_geometry_and_sorts_newest_event_first():
    result = EarthEventsService(
        http_client=make_client(lambda request: httpx.Response(200, json=EONET_PAYLOAD))
    ).get_events(limit=1)
    assert result.count == 1
    assert result.events[0].id == "EONET_1"
    assert result.events[0].latest_geometry.date == datetime(
        2026, 9, 4, 12, tzinfo=timezone.utc
    )


def test_malformed_eonet_response_is_unavailable_without_invented_events():
    result = EarthEventsService(
        http_client=make_client(lambda request: httpx.Response(200, json={"items": []}))
    ).get_events()
    assert result.freshness == ClimateFreshness.unavailable
    assert result.events == []
    assert result.count == 0


@pytest.mark.parametrize(
    "handler",
    [
        lambda request: httpx.Response(503),
        lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("slow", request=request)),
    ],
)
def test_eonet_provider_failures_are_unavailable_without_a_real_cache(handler):
    result = EarthEventsService(http_client=make_client(handler)).get_events()
    assert result.freshness == ClimateFreshness.unavailable
    assert result.events == []


def test_eonet_timeout_uses_expired_real_cache_as_stale():
    clock = Clock()
    should_fail = False

    def handler(request):
        if should_fail:
            raise httpx.ReadTimeout("slow", request=request)
        return httpx.Response(200, json=EONET_PAYLOAD)

    service = EarthEventsService(
        http_client=make_client(handler),
        cache=TTLCache(clock=clock),
        ttl_seconds=60,
        clock=clock,
    )
    current = service.get_events()
    should_fail = True
    clock.now += timedelta(seconds=61)
    stale = service.get_events()

    assert stale.freshness == ClimateFreshness.stale
    assert stale.source.freshness == ClimateFreshness.stale
    assert all(event.source.freshness == ClimateFreshness.stale for event in stale.events)
    assert stale.events[0].title == current.events[0].title
    assert stale.fetched_at == current.fetched_at


def test_event_language_does_not_add_a_climate_attribution_claim():
    result = EarthEventsService(
        http_client=make_client(lambda request: httpx.Response(200, json=EONET_PAYLOAD))
    ).get_events()
    assert "does not establish" in result.attribution_disclaimer
    assert "separate scientific analysis" in result.attribution_disclaimer
    assert "climate disaster" not in result.model_dump_json().lower()
