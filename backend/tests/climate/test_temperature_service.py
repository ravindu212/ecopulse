from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.schemas.climate import ClimateDataType, ClimateFreshness
from app.services.climate.cache import TTLCache
from app.services.climate.co2_service import ClimateDataParseError
from app.services.climate.http_client import ProviderHttpClient
from app.services.climate.providers.noaa_ncei import parse_noaa_global_temperature
from app.services.climate.temperature_service import GlobalTemperatureService


NOAA_TEMPERATURE_DATA = """2026  6  0.521217 -999 -999
invalid partial row
2025 12  0.436583 -999 -999
2026  7  0.602222 -999 -999
2026 13  9.999999 -999 -999
2026  5  not-a-number -999 -999
"""


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 5, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def make_client(handler):
    return ProviderHttpClient(client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_parser_returns_chronological_bounded_monthly_anomalies():
    points = parse_noaa_global_temperature(NOAA_TEMPERATURE_DATA, history_limit=2)

    assert [point.period for point in points] == ["June 2026", "July 2026"]
    assert [point.value for point in points] == [0.521217, 0.602222]
    assert all(point.unit == "°C anomaly" for point in points)


def test_parser_rejects_response_without_real_numeric_data():
    with pytest.raises(ClimateDataParseError, match="no valid global temperature"):
        parse_noaa_global_temperature("bad row\n2026 13 -999", history_limit=60)


def test_temperature_service_exposes_latest_version_baseline_and_source():
    result = GlobalTemperatureService(
        http_client=make_client(
            lambda request: httpx.Response(200, text=NOAA_TEMPERATURE_DATA)
        )
    ).get_global_temperature()

    assert result.freshness == ClimateFreshness.current
    assert result.latest_anomaly is not None
    assert result.latest_anomaly.value == 0.602222
    assert result.latest_anomaly.period == "July 2026"
    assert result.latest_anomaly.unit == "°C anomaly"
    assert result.baseline == "1991-2020 monthly climatology"
    assert result.product_version == "6.1.0"
    assert result.source.publisher == "NOAA National Centers for Environmental Information"
    assert result.source.data_type == ClimateDataType.analysis
    assert "kelvin" in result.methodology_note


@pytest.mark.parametrize(
    "handler",
    [
        lambda request: httpx.Response(503),
        lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("slow", request=request)),
    ],
)
def test_temperature_provider_failure_never_fabricates_values(handler):
    result = GlobalTemperatureService(http_client=make_client(handler)).get_global_temperature()

    assert result.freshness == ClimateFreshness.unavailable
    assert result.latest_anomaly is None
    assert result.historical_series == []
    assert result.source.freshness == ClimateFreshness.unavailable


def test_expired_temperature_cache_is_returned_as_stale():
    clock = Clock()
    requests = 0

    def handler(request):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(200, text=NOAA_TEMPERATURE_DATA)
        raise httpx.ReadTimeout("slow", request=request)

    service = GlobalTemperatureService(
        http_client=make_client(handler),
        cache=TTLCache(clock=clock),
        ttl_seconds=60,
        clock=clock,
    )
    assert service.get_global_temperature().freshness == ClimateFreshness.current
    clock.now += timedelta(seconds=61)
    stale = service.get_global_temperature()

    assert stale.freshness == ClimateFreshness.stale
    assert stale.latest_anomaly is not None
    assert stale.latest_anomaly.value == 0.602222
    assert stale.latest_anomaly.source.freshness == ClimateFreshness.stale
    assert stale.source.freshness == ClimateFreshness.stale
