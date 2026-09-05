from datetime import datetime, timezone

import httpx

from app.api.routes.climate import get_co2_service, get_enso_service, get_events_service
from app.main import app
from app.schemas.climate import (
    CO2Response,
    ClimateFreshness,
    ClimateNumericDatum,
    EarthEventsResponse,
)
from app.services.climate.source_registry import (
    EARTH_EVENT_ATTRIBUTION_DISCLAIMER,
    eonet_source,
    noaa_source,
)
from app.services.climate.enso_service import ENSOService
from app.services.climate.http_client import ProviderHttpClient


NOW = datetime(2026, 9, 5, tzinfo=timezone.utc)


class FakeCO2Service:
    def get_co2(self):
        source = noaa_source("https://gml.noaa.gov/data.csv", ClimateFreshness.current, NOW, NOW)
        return CO2Response(
            latest=ClimateNumericDatum(
                label="Estimated global atmospheric CO2 trend",
                value=427.3,
                unit="ppm",
                observed_at=NOW,
                source=source,
            ),
            series=[],
            source=source,
            status=ClimateFreshness.current,
        )


class FakeEventsService:
    def get_events(self, category=None, days=30, limit=20):
        source = eonet_source("https://eonet.gsfc.nasa.gov/api/v3/events", ClimateFreshness.current, NOW)
        return EarthEventsResponse(
            events=[],
            count=0,
            source=source,
            fetched_at=NOW,
            freshness=ClimateFreshness.current,
            attribution_disclaimer=EARTH_EVENT_ATTRIBUTION_DISCLAIMER,
        )


class FakeENSOService:
    def get_enso(self):
        client = ProviderHttpClient(
            client=httpx.Client(
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(
                        200,
                        text=(
                            "Week SST SSTA\n"
                            " 26AUG2026 25.0 4.2 28.3 3.4 29.4 2.6 29.6 1.0\n"
                        ),
                    )
                )
            )
        )
        return ENSOService(http_client=client).get_enso()


def test_climate_endpoints_are_public_and_need_no_jwt(client):
    app.dependency_overrides[get_co2_service] = lambda: FakeCO2Service()
    app.dependency_overrides[get_events_service] = lambda: FakeEventsService()
    app.dependency_overrides[get_enso_service] = lambda: FakeENSOService()

    co2_response = client.get("/api/v1/climate/co2")
    events_response = client.get("/api/v1/climate/events")
    enso_response = client.get("/api/v1/climate/enso")

    assert co2_response.status_code == 200
    assert co2_response.json()["latest"]["value"] == 427.3
    assert events_response.status_code == 200
    assert events_response.json()["count"] == 0
    assert enso_response.status_code == 200
    assert enso_response.json()["observations"]["latest_nino34"]["value"] == 2.6
    assert enso_response.json()["status"]["source"]["data_type"] == "analysis"
    assert enso_response.json()["outlook"]["wmo"]["source"]["data_type"] == "analysis"
    assert (
        enso_response.json()["outlook"]["wmo"]["probabilities"][0]["source"]["data_type"]
        == "forecast"
    )


def test_event_query_bounds_and_category_are_validated(client):
    app.dependency_overrides[get_events_service] = lambda: FakeEventsService()

    assert client.get("/api/v1/climate/events?limit=0").status_code == 422
    assert client.get("/api/v1/climate/events?limit=101").status_code == 422
    assert client.get("/api/v1/climate/events?days=0").status_code == 422
    assert client.get("/api/v1/climate/events?days=366").status_code == 422
    assert client.get("/api/v1/climate/events?category=wildfires%26status=closed").status_code == 422
