from datetime import datetime, timedelta, timezone

import httpx

from app.api.routes.climate import get_overview_service
from app.main import app
from app.schemas.climate import ClimateFreshness
from app.services.climate.co2_service import CO2Service
from app.services.climate.enso_service import ENSOService
from app.services.climate.events_service import EarthEventsService
from app.services.climate.http_client import ProviderHttpClient
from app.services.climate.overview_service import ClimateOverviewService
from app.services.climate.outlook_service import SeasonalOutlookService
from app.services.climate.temperature_service import GlobalTemperatureService


CO2_DATA = """year,month,day,trend
2026,9,1,427.1
"""
ENSO_DATA = """Week SST SSTA
 26AUG2026 25.0 4.2 28.3 3.4 29.4 2.6 29.6 1.0
"""
TEMPERATURE_DATA = """2026 6 0.52 -999
2026 7 0.60 -999
"""
EVENTS_DATA = {"events": []}


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 5, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def provider(handler):
    return ProviderHttpClient(client=httpx.Client(transport=httpx.MockTransport(handler)))


def text_handler(content: str, counter: dict[str, int], name: str):
    def handler(request):
        counter[name] = counter.get(name, 0) + 1
        return httpx.Response(200, text=content)

    return handler


def json_handler(payload, counter: dict[str, int], name: str):
    def handler(request):
        counter[name] = counter.get(name, 0) + 1
        return httpx.Response(200, json=payload)

    return handler


def build_overview(
    *,
    co2_handler=None,
    enso_handler=None,
    temperature_handler=None,
    events_handler=None,
    clock=None,
    temperature_ttl_seconds=43_200,
    outlook_service=None,
):
    counter: dict[str, int] = {}
    current_clock = clock or Clock()
    service = ClimateOverviewService(
        co2_service=CO2Service(
            http_client=provider(
                co2_handler or text_handler(CO2_DATA, counter, "co2")
            ),
            clock=current_clock,
        ),
        enso_service=ENSOService(
            http_client=provider(
                enso_handler or text_handler(ENSO_DATA, counter, "enso")
            ),
            clock=current_clock,
        ),
        temperature_service=GlobalTemperatureService(
            http_client=provider(
                temperature_handler
                or text_handler(TEMPERATURE_DATA, counter, "temperature")
            ),
            clock=current_clock,
            ttl_seconds=temperature_ttl_seconds,
        ),
        events_service=EarthEventsService(
            http_client=provider(
                events_handler or json_handler(EVENTS_DATA, counter, "events")
            ),
            clock=current_clock,
        ),
        outlook_service=outlook_service
        or SeasonalOutlookService(clock=current_clock),
        clock=current_clock,
    )
    return service, counter


def test_overview_composes_existing_services_once_and_retains_sources():
    service, counter = build_overview()

    result = service.get_overview()

    assert counter == {"co2": 1, "enso": 1, "temperature": 1, "events": 1}
    assert result.co2.latest.value == 427.1
    assert result.enso.latest_nino34.value == 2.6
    assert result.global_temperature.latest_anomaly.value == 0.60
    assert result.ocean.indicator == "extra_polar_sea_surface_temperature"
    assert result.sea_ice.arctic.indicator == "arctic_sea_ice_extent"
    assert result.sea_ice.antarctic.indicator == "antarctic_sea_ice_extent"
    assert result.earth_events.returned_event_count == 0
    assert result.earth_events.window_days == 30
    assert result.earth_events.result_limit == 10
    assert result.seasonal_outlook.period == "September-November 2026"
    assert result.seasonal_outlook.validity.value == "current"
    assert result.availability.stale_components == []
    assert result.availability.unavailable_components == []
    publishers = {source.publisher for source in result.sources}
    assert "NOAA Global Monitoring Laboratory" in publishers
    assert "NOAA Climate Prediction Center" in publishers
    assert "NOAA National Centers for Environmental Information" in publishers
    assert "NASA Earth Science Data Systems" in publishers
    assert "Copernicus Climate Change Service" in publishers
    assert "World Meteorological Organization" in publishers
    payload = result.model_dump()
    assert "user" not in payload
    assert "score" not in payload


def test_overview_survives_one_unavailable_component():
    service, _ = build_overview(
        temperature_handler=lambda request: httpx.Response(503)
    )

    result = service.get_overview()

    assert result.global_temperature.freshness == ClimateFreshness.unavailable
    assert result.global_temperature.latest_anomaly is None
    assert result.co2.freshness == ClimateFreshness.current
    assert result.enso.observation_freshness == ClimateFreshness.current
    assert result.availability.unavailable_components == ["global_temperature"]


def test_overview_survives_multiple_unavailable_components():
    failing = lambda request: httpx.Response(503)
    service, _ = build_overview(
        co2_handler=failing,
        enso_handler=failing,
        events_handler=failing,
    )

    result = service.get_overview()

    assert set(result.availability.unavailable_components) == {
        "co2",
        "enso_observations",
        "earth_events",
    }
    assert "enso_analysis" in result.availability.available_components
    assert "climate_bulletin" in result.availability.available_components
    assert result.global_temperature.latest_anomaly is not None


def test_overview_reports_a_stale_component_honestly():
    clock = Clock()
    requests = 0

    def temperature_handler(request):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(200, text=TEMPERATURE_DATA)
        raise httpx.ReadTimeout("slow", request=request)

    service, _ = build_overview(
        temperature_handler=temperature_handler,
        clock=clock,
        temperature_ttl_seconds=60,
    )
    assert service.get_overview().global_temperature.freshness == ClimateFreshness.current
    clock.now += timedelta(seconds=61)

    result = service.get_overview()

    assert result.global_temperature.freshness == ClimateFreshness.stale
    assert result.availability.stale_components == ["global_temperature"]
    assert "global_temperature" not in result.availability.available_components


def test_overview_endpoint_is_public(client):
    service, _ = build_overview()
    app.dependency_overrides[get_overview_service] = lambda: service

    response = client.get("/api/v1/climate/overview")

    assert response.status_code == 200
    assert response.json()["global_temperature"]["latest_anomaly"]["value"] == 0.60
    assert "climate_bulletin" in response.json()["availability"]["available_components"]


def test_overview_survives_unavailable_seasonal_outlook():
    service, _ = build_overview(
        outlook_service=SeasonalOutlookService(records=(), clock=Clock())
    )

    result = service.get_overview()

    assert result.seasonal_outlook is None
    assert "seasonal_outlook" in result.availability.unavailable_components
    assert result.global_temperature.latest_anomaly is not None
    assert result.latest_bulletin.temperature_context.headline
