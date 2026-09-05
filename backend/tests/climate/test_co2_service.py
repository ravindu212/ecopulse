from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.schemas.climate import ClimateFreshness
from app.services.climate.cache import TTLCache
from app.services.climate.co2_service import CO2Service, parse_noaa_global_trend_csv
from app.services.climate.http_client import ProviderHttpClient


NOAA_CSV = """# NOAA metadata
# Values are estimates
year,month,day,decimal,trend
2026,9,1,2026.667,427.10
malformed,row
2026,9,3,2026.673,427.30
2026,9,2,2026.670,not-a-number
"""


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 5, 10, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def make_client(handler):
    return ProviderHttpClient(client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_noaa_valid_response_is_numeric_attributed_ordered_and_bounded():
    clock = Clock()
    service = CO2Service(
        http_client=make_client(lambda request: httpx.Response(200, text=NOAA_CSV)),
        cache=TTLCache(clock=clock),
        history_limit=1,
        clock=clock,
    )

    result = service.get_co2()
    encoded = result.model_dump(mode="json")

    assert result.status == ClimateFreshness.current
    assert result.latest.value == 427.30
    assert isinstance(encoded["latest"]["value"], float)
    assert result.latest.unit == "ppm"
    assert result.latest.observed_at == datetime(2026, 9, 3, tzinfo=timezone.utc)
    assert len(result.series) == 1
    assert result.source.publisher == "NOAA Global Monitoring Laboratory"
    assert result.source.source_url.endswith("co2_trend_gl.csv")
    assert result.source.data_type.value == "estimate"
    assert "preliminary" in result.source.methodology_note


def test_noaa_parser_skips_malformed_rows_and_orders_dates():
    content = """year,month,day,trend
2026,9,3,427.3
2026,13,1,999
2026,9,1,427.1
2026,9,2,n/a
"""
    points = parse_noaa_global_trend_csv(content, history_limit=60)
    assert [point.value for point in points] == [427.1, 427.3]


@pytest.mark.parametrize(
    "handler",
    [
        lambda request: httpx.Response(502),
        lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("slow", request=request)),
    ],
)
def test_noaa_failure_without_real_cache_is_unavailable_and_never_fabricated(handler):
    result = CO2Service(http_client=make_client(handler)).get_co2()
    assert result.status == ClimateFreshness.unavailable
    assert result.latest is None
    assert result.series == []


def test_malformed_noaa_response_is_unavailable():
    service = CO2Service(
        http_client=make_client(lambda request: httpx.Response(200, text="year,value\n2026,nope"))
    )
    assert service.get_co2().status == ClimateFreshness.unavailable


def test_expired_real_noaa_value_is_returned_as_stale_after_failure():
    clock = Clock()
    should_fail = False

    def handler(request):
        if should_fail:
            raise httpx.ReadTimeout("slow", request=request)
        return httpx.Response(200, text=NOAA_CSV)

    service = CO2Service(
        http_client=make_client(handler),
        cache=TTLCache(clock=clock),
        ttl_seconds=60,
        clock=clock,
    )
    current = service.get_co2()
    should_fail = True
    clock.now += timedelta(seconds=61)
    stale = service.get_co2()

    assert stale.status == ClimateFreshness.stale
    assert stale.source.freshness == ClimateFreshness.stale
    assert stale.latest.source.freshness == ClimateFreshness.stale
    assert stale.latest.value == current.latest.value
    assert stale.source.fetched_at == current.source.fetched_at
