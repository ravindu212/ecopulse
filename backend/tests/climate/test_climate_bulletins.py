from datetime import date

from app.schemas.climate import ClimateDataType
from app.services.climate.bulletin_service import ClimateBulletinService
from app.services.climate.curated.climate_bulletins import (
    CuratedClimateBulletin,
    CuratedClimateContext,
    select_latest_climate_bulletin,
)


def context(indicator: str, headline: str) -> CuratedClimateContext:
    return CuratedClimateContext(
        indicator=indicator,
        headline=headline,
        summary=f"Concise original summary for {indicator}.",
    )


def bulletin(issue_date: date, suffix: str) -> CuratedClimateBulletin:
    return CuratedClimateBulletin(
        source_name=f"Test bulletin {suffix}",
        publisher="Copernicus Climate Change Service",
        issue_date=issue_date,
        reference_period=f"Reference {suffix}",
        verified_at=issue_date,
        source_url=f"https://provider.test/{suffix}",
        temperature_context=context("temperature", f"Temperature {suffix}"),
        sea_surface_temperature_context=context("ocean", f"Ocean {suffix}"),
        arctic_sea_ice_context=context("arctic", f"Arctic {suffix}"),
        antarctic_sea_ice_context=context("antarctic", f"Antarctic {suffix}"),
        precipitation_extremes_note=None,
    )


def test_latest_verified_bulletin_is_selected_by_issue_date():
    older = bulletin(date(2025, 1, 1), "older")
    newer = bulletin(date(2025, 2, 1), "newer")

    assert select_latest_climate_bulletin((newer, older)) is newer


def test_bulletin_preserves_distinct_contexts_and_optional_fields():
    record = bulletin(date(2025, 2, 1), "selected")
    result = ClimateBulletinService(bulletins=(record,)).get_latest()

    assert result.publisher == record.publisher
    assert result.issue_date == record.issue_date
    assert result.reference_period == record.reference_period
    assert result.verified_at == record.verified_at
    assert result.source_url == record.source_url
    assert result.temperature_context.headline == "Temperature selected"
    assert result.sea_surface_temperature_context.headline == "Ocean selected"
    assert result.arctic_sea_ice_context.headline == "Arctic selected"
    assert result.antarctic_sea_ice_context.headline == "Antarctic selected"
    assert result.precipitation_extremes_note is None
    assert result.temperature_context.rank is None
    assert result.source.data_type == ClimateDataType.analysis
    assert all(
        item.source.data_type == ClimateDataType.analysis
        for item in (
            result.temperature_context,
            result.sea_surface_temperature_context,
            result.arctic_sea_ice_context,
            result.antarctic_sea_ice_context,
        )
    )
    assert all(
        len(item.summary) < 200
        for item in (
            result.temperature_context,
            result.sea_surface_temperature_context,
            result.arctic_sea_ice_context,
            result.antarctic_sea_ice_context,
        )
    )
