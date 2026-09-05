from datetime import datetime, time, timezone

from app.schemas.climate import ClimateBulletin, IssuedClimateContext
from app.services.climate.curated.climate_bulletins import (
    CuratedClimateBulletin,
    CuratedClimateContext,
    select_latest_climate_bulletin,
)
from app.services.climate.source_registry import (
    COPERNICUS_BULLETIN_METHODOLOGY,
    copernicus_bulletin_source,
)


def _build_context(
    context: CuratedClimateContext,
    bulletin: CuratedClimateBulletin,
    published_at: datetime,
) -> IssuedClimateContext:
    source = copernicus_bulletin_source(
        f"{bulletin.source_name} - {context.indicator}",
        context.source_url or bulletin.source_url,
        published_at,
    )
    return IssuedClimateContext(
        indicator=context.indicator,
        headline=context.headline,
        summary=context.summary,
        reference_period=bulletin.reference_period,
        rank=context.rank,
        rank_qualifier=context.rank_qualifier,
        source=source,
    )


class ClimateBulletinService:
    def __init__(
        self,
        bulletins: tuple[CuratedClimateBulletin, ...] | None = None,
    ):
        self._bulletins = bulletins

    def get_latest(self) -> ClimateBulletin:
        record = (
            select_latest_climate_bulletin()
            if self._bulletins is None
            else select_latest_climate_bulletin(self._bulletins)
        )
        published_at = datetime.combine(
            record.issue_date, time.min, tzinfo=timezone.utc
        )
        source = copernicus_bulletin_source(
            record.source_name, record.source_url, published_at
        )
        return ClimateBulletin(
            publisher=record.publisher,
            issue_date=record.issue_date,
            reference_period=record.reference_period,
            verified_at=record.verified_at,
            source_url=record.source_url,
            temperature_context=_build_context(
                record.temperature_context, record, published_at
            ),
            sea_surface_temperature_context=_build_context(
                record.sea_surface_temperature_context, record, published_at
            ),
            arctic_sea_ice_context=_build_context(
                record.arctic_sea_ice_context, record, published_at
            ),
            antarctic_sea_ice_context=_build_context(
                record.antarctic_sea_ice_context, record, published_at
            ),
            precipitation_extremes_note=record.precipitation_extremes_note,
            source=source,
            latest_known_issue=True,
            methodology_note=COPERNICUS_BULLETIN_METHODOLOGY,
        )
