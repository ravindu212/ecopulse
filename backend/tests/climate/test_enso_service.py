from datetime import date, datetime, timedelta, timezone

import httpx
import pytest
from pydantic import ValidationError

from app.schemas.climate import (
    ClimateDataType,
    ClimateFreshness,
    ENSOPhase,
    ENSOProbability,
    ENSORegion,
)
from app.services.climate.cache import TTLCache
from app.services.climate.co2_service import ClimateDataParseError
from app.services.climate.curated.enso_bulletins import (
    CuratedENSOBulletin,
    CuratedProbability,
)
from app.services.climate.enso_service import ENSOService, normalize_enso_phase
from app.services.climate.http_client import ProviderHttpClient
from app.services.climate.providers.noaa_cpc import parse_cpc_weekly_enso


CPC_WEEKLY_DATA = """Weekly SST data starts week centered on 2Sept1981
                Nino1+2      Nino3        Nino34        Nino4
 Week          SST SSTA     SST SSTA     SST SSTA     SST SSTA
 03JUL2026     25.7 3.3     28.2 2.0     29.2 1.7     29.9 1.1
 malformed row that should be ignored
 26JUN2026     25.9-0.3     28.4-0.2     29.3 0.8     30.0 1.2
 10JUL2026     25.5 3.4     28.2 2.2     29.3 2.0     30.0 1.2
"""


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 5, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def make_client(handler):
    return ProviderHttpClient(client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_cpc_weekly_parser_reads_all_regions_and_only_anomalies():
    records = parse_cpc_weekly_enso(CPC_WEEKLY_DATA)

    assert [record.observed_at.date().isoformat() for record in records] == [
        "2026-06-26",
        "2026-07-03",
        "2026-07-10",
    ]
    assert records[0].anomalies == {
        ENSORegion.nino_1_2: -0.3,
        ENSORegion.nino_3: -0.2,
        ENSORegion.nino_3_4: 0.8,
        ENSORegion.nino_4: 1.2,
    }
    assert records[-1].anomalies[ENSORegion.nino_3_4] == 2.0
    assert 29.3 not in records[-1].anomalies.values()


def test_cpc_parser_rejects_a_response_without_valid_rows():
    with pytest.raises(ClimateDataParseError, match="no valid ENSO observations"):
        parse_cpc_weekly_enso("Week SST SSTA\n10BAD2026 1 2 3")


def test_enso_observations_are_bounded_typed_and_source_attributed():
    service = ENSOService(
        http_client=make_client(lambda request: httpx.Response(200, text=CPC_WEEKLY_DATA)),
        history_limit=2,
    )

    result = service.get_enso()

    assert result.observations.freshness == ClimateFreshness.current
    assert result.observation_freshness == ClimateFreshness.current
    assert len(result.observations.nino34_series) == 2
    assert [point.observed_at.date().isoformat() for point in result.observations.nino34_series] == [
        "2026-07-03",
        "2026-07-10",
    ]
    latest = result.observations.latest_nino34
    assert latest is not None
    assert latest.region == ENSORegion.nino_3_4
    assert latest.value == 2.0
    assert latest.unit == "°C anomaly"
    assert latest.period == "Week centered on 2026-07-10"
    assert latest.source.publisher == "NOAA Climate Prediction Center"
    assert latest.source.data_type == ClimateDataType.observation
    assert latest.source.baseline == "1991-2020 weekly climatological means"
    assert {item.region for item in result.observations.regions} == set(ENSORegion)


@pytest.mark.parametrize(
    "handler",
    [
        lambda request: httpx.Response(503),
        lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("slow", request=request)),
    ],
)
def test_provider_failure_has_no_fabricated_observation_but_keeps_issued_context(handler):
    result = ENSOService(http_client=make_client(handler)).get_enso()

    assert result.observations.freshness == ClimateFreshness.unavailable
    assert result.observations.latest_nino34 is None
    assert result.observations.regions == []
    assert result.observations.nino34_series == []
    assert result.status.source.data_type == ClimateDataType.analysis
    assert result.outlook.noaa.source.data_type == ClimateDataType.analysis
    assert result.outlook.wmo.source.data_type == ClimateDataType.analysis
    assert result.outlook.noaa.probabilities[0].source.data_type == ClimateDataType.forecast
    assert result.outlook.wmo.probabilities[0].source.data_type == ClimateDataType.forecast


def test_expired_real_observations_are_returned_as_stale_on_refresh_failure():
    clock = Clock()
    requests = 0

    def handler(request):
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(200, text=CPC_WEEKLY_DATA)
        raise httpx.ReadTimeout("slow", request=request)

    service = ENSOService(
        http_client=make_client(handler),
        cache=TTLCache(clock=clock),
        ttl_seconds=60,
        clock=clock,
    )
    current = service.get_enso()
    clock.now += timedelta(seconds=61)
    stale = service.get_enso()

    assert current.observations.freshness == ClimateFreshness.current
    assert stale.observations.freshness == ClimateFreshness.stale
    assert stale.observations.source.freshness == ClimateFreshness.stale
    assert stale.observations.latest_nino34.source.freshness == ClimateFreshness.stale
    assert all(
        item.source.freshness == ClimateFreshness.stale
        for item in stale.observations.nino34_series
    )


@pytest.mark.parametrize(
    ("wording", "expected"),
    [
        ("El Niño Advisory", ENSOPhase.el_nino),
        ("La Nina Advisory", ENSOPhase.la_nina),
        ("ENSO-neutral", ENSOPhase.neutral),
        ("El Niño Watch", ENSOPhase.unknown),
        ("La Niña Advisory / El Niño Watch", ENSOPhase.la_nina),
        ("unparseable", ENSOPhase.unknown),
        (None, ENSOPhase.unknown),
    ],
)
def test_status_normalization_is_conservative(wording, expected):
    assert normalize_enso_phase(wording) == expected


def test_curated_status_and_outlooks_preserve_issue_metadata_and_attribution():
    noaa_bulletin = CuratedENSOBulletin(
        source_name="Test NOAA discussion",
        publisher="NOAA Climate Prediction Center",
        issue_date=date(2024, 1, 11),
        source_url="https://cpc.example/issued-discussion",
        verified_at=date(2024, 1, 12),
        alert_status="La Niña Advisory",
        headline="Test NOAA headline.",
        summary="Concise test NOAA summary.",
        valid_period="Test NOAA period",
        probabilities=(
            CuratedProbability(
                label="Test NOAA outcome",
                probability=70,
                qualifier="greater_than",
                valid_period="Test NOAA period",
            ),
        ),
    )
    wmo_bulletin = CuratedENSOBulletin(
        source_name="Test WMO update",
        publisher="World Meteorological Organization",
        issue_date=date(2024, 2, 1),
        source_url="https://wmo.example/issued-update",
        verified_at=date(2024, 2, 2),
        alert_status=None,
        headline="Test WMO headline.",
        summary="Concise test WMO summary.",
        valid_period="Test WMO period",
        probabilities=(
            CuratedProbability(
                label="Test WMO outcome",
                probability=80,
                qualifier="near",
                valid_period="Test WMO period",
            ),
        ),
    )
    result = ENSOService(
        http_client=make_client(lambda request: httpx.Response(200, text=CPC_WEEKLY_DATA)),
        noaa_bulletin=noaa_bulletin,
        wmo_bulletin=wmo_bulletin,
    ).get_enso()

    assert result.status.alert_status == "La Niña Advisory"
    assert result.status.enso_phase == ENSOPhase.la_nina
    assert result.status.issued_at == noaa_bulletin.issue_date
    assert result.status.source.publisher == "NOAA Climate Prediction Center"
    assert result.outlook.noaa.issue_date == noaa_bulletin.issue_date
    assert result.outlook.wmo.issue_date == wmo_bulletin.issue_date
    assert result.outlook.noaa.verified_at == noaa_bulletin.verified_at
    assert result.outlook.wmo.verified_at == wmo_bulletin.verified_at
    assert result.outlook.wmo.source.publisher == "World Meteorological Organization"
    assert result.outlook.noaa.probabilities[0].probability == 70
    assert result.outlook.noaa.probabilities[0].qualifier == "greater_than"
    assert result.outlook.wmo.probabilities[0].probability == 80
    assert result.outlook.wmo.probabilities[0].qualifier == "near"
    assert all(len(outlook.summary) < 300 for outlook in (result.outlook.noaa, result.outlook.wmo))
    assert "EcoPulse prediction" in result.outlook.wmo.methodology_note
    assert any("not forecasts" in note for note in result.explanatory_notes)
    assert any("does not determine impacts" in note for note in result.explanatory_notes)


def test_absent_probability_is_none_not_zero_and_bounds_are_validated():
    probability = ENSOProbability(
        label="No explicit probability supplied",
        valid_period="Unspecified",
        issued_at="2026-09-03",
        source=ENSOService(
            http_client=make_client(lambda request: httpx.Response(200, text=CPC_WEEKLY_DATA))
        ).get_enso().outlook.wmo.source,
    )
    assert probability.probability is None

    with pytest.raises(ValidationError):
        ENSOProbability(
            label="Invalid",
            probability=101,
            valid_period="Unspecified",
            issued_at="2026-09-03",
            source=probability.source,
        )
