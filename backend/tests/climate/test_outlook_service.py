from dataclasses import replace
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.api.routes.climate import get_outlook_service
from app.main import app
from app.schemas.climate import (
    ClimateDataType,
    ProbabilityQualifier,
    SeasonalOutlookValidity,
    SeasonalProbability,
)
from app.services.climate.curated.seasonal_outlooks import (
    CuratedForecastPeriod,
    CuratedOceanDriver,
    CuratedSeasonalProbability,
    WMO_GSCU_SON_2026,
)
from app.services.climate.outlook_service import (
    SeasonalOutlookService,
    SeasonalOutlookUnavailableError,
    determine_outlook_validity,
    select_seasonal_outlook,
)


NOW = datetime(2026, 9, 5, tzinfo=timezone.utc)


def clock_at(value: datetime):
    return lambda: value


@pytest.fixture
def fake_current_record():
    return replace(
        WMO_GSCU_SON_2026,
        source_name="Fixture seasonal issue",
        issue_date=date(2031, 3, 4),
        verified_at=date(2031, 3, 5),
        source_url="https://example.test/seasonal/2031-mam",
        forecast_period=CuratedForecastPeriod(
            label="March-May 2031",
            start_date=date(2031, 3, 1),
            end_date=date(2031, 5, 31),
        ),
        baseline="2001-2020 fixture baseline",
        enso=replace(
            WMO_GSCU_SON_2026.enso,
            forecast_value=1.7,
            valid_period="March-May 2031 seasonal mean",
        ),
        iod=replace(
            WMO_GSCU_SON_2026.iod,
            forecast_value=0.4,
            valid_period="March-May 2031 seasonal mean",
        ),
    )


def test_outlook_record_preserves_issue_driver_and_source_fields(fake_current_record):
    service = SeasonalOutlookService(
        records=(fake_current_record,),
        clock=clock_at(datetime(2031, 3, 10, tzinfo=timezone.utc)),
    )

    result = service.get_outlook()

    assert result.issue.publisher == "World Meteorological Organization"
    assert result.issue.issue_date == date(2031, 3, 4)
    assert result.issue.verified_at == date(2031, 3, 5)
    assert result.issue.source_url == "https://example.test/seasonal/2031-mam"
    assert result.issue.data_type == ClimateDataType.forecast
    assert result.forecast_period.label == "March-May 2031"
    assert result.forecast_period.validity == SeasonalOutlookValidity.current
    assert result.baseline == "2001-2020 fixture baseline"
    assert result.oceanic_drivers.enso.forecast_value == 1.7
    assert result.oceanic_drivers.enso.source.data_type == ClimateDataType.forecast
    assert result.oceanic_drivers.iod.forecast_value == 0.4
    assert result.oceanic_drivers.iod.phase.value == "positive"
    assert result.temperature.narrative
    assert result.precipitation.narrative
    assert result.sources[0].publisher == "World Meteorological Organization"


def test_outlook_allows_missing_optional_iod(fake_current_record):
    record = replace(fake_current_record, iod=None)

    result = SeasonalOutlookService(
        records=(record,),
        clock=clock_at(datetime(2031, 3, 10, tzinfo=timezone.utc)),
    ).get_outlook()

    assert result.oceanic_drivers.iod is None


@pytest.mark.parametrize(
    ("qualifier", "probability"),
    [
        ("exact", 55.5),
        ("greater_than", 70.0),
        ("near", 100.0),
        ("not_specified", None),
    ],
)
def test_probability_values_and_qualifiers_are_preserved(
    fake_current_record, qualifier, probability
):
    tendency = CuratedSeasonalProbability(
        category="above_normal",
        probability=probability,
        qualifier=qualifier,
        valid_period="March-May 2031",
        region="Fixture region",
    )
    record = replace(
        fake_current_record,
        temperature_outlook=replace(
            fake_current_record.temperature_outlook, tendencies=(tendency,)
        ),
    )

    result = SeasonalOutlookService(
        records=(record,),
        clock=clock_at(datetime(2031, 3, 10, tzinfo=timezone.utc)),
    ).get_outlook()
    returned = result.temperature.tendencies[0]

    assert returned.probability == probability
    assert returned.qualifier == ProbabilityQualifier(qualifier)
    assert returned.probability is None or isinstance(returned.probability, float)


@pytest.mark.parametrize("probability", [-0.1, 100.1])
def test_curated_probability_rejects_values_outside_percent_range(probability):
    with pytest.raises(ValueError):
        CuratedSeasonalProbability(
            category="above_normal",
            probability=probability,
            qualifier="exact",
            valid_period="Fixture period",
            region="Fixture region",
        )


def test_api_probability_model_also_rejects_values_over_100(fake_current_record):
    source = SeasonalOutlookService(
        records=(fake_current_record,),
        clock=clock_at(datetime(2031, 3, 10, tzinfo=timezone.utc)),
    ).get_outlook().sources[0]

    with pytest.raises(ValidationError):
        SeasonalProbability(
            category="above_normal",
            probability=101,
            qualifier="exact",
            valid_period="Fixture period",
            region="Fixture region",
            source=source,
        )


def test_validity_is_date_driven_and_not_tied_to_a_named_season(fake_current_record):
    assert (
        determine_outlook_validity(fake_current_record, date(2031, 2, 28))
        == SeasonalOutlookValidity.upcoming
    )
    assert (
        determine_outlook_validity(fake_current_record, date(2031, 4, 10))
        == SeasonalOutlookValidity.current
    )
    assert (
        determine_outlook_validity(fake_current_record, date(2031, 6, 1))
        == SeasonalOutlookValidity.expired
    )


def test_selection_handles_one_issue_and_prefers_newest_current_issue(
    fake_current_record,
):
    older = replace(
        fake_current_record,
        issue_date=date(2031, 3, 1),
        verified_at=date(2031, 3, 2),
        source_url="https://example.test/older",
    )

    assert (
        select_seasonal_outlook(
            (older, fake_current_record), as_of=date(2031, 3, 10)
        )
        == fake_current_record
    )
    assert (
        select_seasonal_outlook((fake_current_record,), date(2031, 3, 10))
        == fake_current_record
    )


def test_selection_prefers_current_period_over_newer_upcoming_issue(
    fake_current_record,
):
    upcoming = replace(
        fake_current_record,
        issue_date=date(2031, 3, 8),
        verified_at=date(2031, 3, 9),
        forecast_period=CuratedForecastPeriod(
            label="June-August 2031",
            start_date=date(2031, 6, 1),
            end_date=date(2031, 8, 31),
        ),
    )

    selected = select_seasonal_outlook(
        (fake_current_record, upcoming), as_of=date(2031, 3, 10)
    )

    assert selected == fake_current_record


def test_service_represents_future_and_expired_issues_honestly(fake_current_record):
    upcoming_record = replace(
        fake_current_record,
        forecast_period=CuratedForecastPeriod(
            label="April-June 2031",
            start_date=date(2031, 4, 1),
            end_date=date(2031, 6, 30),
        ),
    )
    future = SeasonalOutlookService(
        records=(upcoming_record,),
        clock=clock_at(datetime(2031, 3, 10, tzinfo=timezone.utc)),
    ).get_outlook()
    expired = SeasonalOutlookService(
        records=(fake_current_record,),
        clock=clock_at(datetime(2031, 6, 1, tzinfo=timezone.utc)),
    ).get_outlook()

    assert future.forecast_period.validity == SeasonalOutlookValidity.upcoming
    assert expired.forecast_period.validity == SeasonalOutlookValidity.expired
    assert expired.sources[0].freshness.value == "stale"


def test_unverified_or_empty_record_set_is_unavailable(fake_current_record):
    future_verification = replace(
        fake_current_record, verified_at=date(2031, 3, 11)
    )

    with pytest.raises(SeasonalOutlookUnavailableError):
        select_seasonal_outlook((future_verification,), as_of=date(2031, 3, 10))
    with pytest.raises(SeasonalOutlookUnavailableError):
        select_seasonal_outlook((), as_of=date(2031, 3, 10))


def test_outlook_endpoint_is_public_and_keeps_forecast_distinct(client):
    service = SeasonalOutlookService(records=(WMO_GSCU_SON_2026,), clock=clock_at(NOW))
    app.dependency_overrides[get_outlook_service] = lambda: service

    response = client.get("/api/v1/climate/outlook")

    assert response.status_code == 200
    payload = response.json()
    assert payload["issue"]["data_type"] == "forecast"
    assert payload["oceanic_drivers"]["enso"]["source"]["data_type"] == "forecast"
    assert "observations" not in payload
    assert "user" not in payload
    assert "auth" not in payload
    serialized = response.text.casefold()
    assert "exact weather" in serialized
    assert "it will rain more" not in serialized
    assert "daily rain" not in serialized


def test_outlook_endpoint_returns_503_when_no_verified_issue_exists(client):
    app.dependency_overrides[get_outlook_service] = lambda: SeasonalOutlookService(
        records=(), clock=clock_at(NOW)
    )

    response = client.get("/api/v1/climate/outlook")

    assert response.status_code == 503
