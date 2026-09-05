from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CuratedClimateContext:
    indicator: str
    headline: str
    summary: str
    rank: int | None = None
    rank_qualifier: str | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class CuratedClimateBulletin:
    source_name: str
    publisher: str
    issue_date: date
    reference_period: str
    verified_at: date
    source_url: str
    temperature_context: CuratedClimateContext
    sea_surface_temperature_context: CuratedClimateContext
    arctic_sea_ice_context: CuratedClimateContext
    antarctic_sea_ice_context: CuratedClimateContext
    precipitation_extremes_note: str | None = None


COPERNICUS_JULY_2026 = CuratedClimateBulletin(
    source_name="Copernicus Climate Bulletin - July 2026",
    publisher="Copernicus Climate Change Service",
    issue_date=date(2026, 8, 10),
    reference_period="July 2026",
    verified_at=date(2026, 9, 5),
    source_url=(
        "https://climate.copernicus.eu/climate-bulletin"
    ),
    temperature_context=CuratedClimateContext(
        indicator="global_surface_air_temperature",
        headline="July 2026 was jointly the second-warmest July in ERA5.",
        summary=(
            "Copernicus placed July 2026 alongside July 2024, behind the July 2023 "
            "record in its ERA5 analysis."
        ),
        rank=2,
        rank_qualifier="joint",
        source_url="https://climate.copernicus.eu/surface-air-temperature-july-2026",
    ),
    sea_surface_temperature_context=CuratedClimateContext(
        indicator="extra_polar_sea_surface_temperature",
        headline="Extra-polar sea-surface temperature set a July record.",
        summary=(
            "Copernicus reported the highest July sea-surface temperature in its "
            "record for oceans between 60°S and 60°N."
        ),
        rank=1,
        source_url=(
            "https://climate.copernicus.eu/exceptionally-hot-and-dry-conditions-"
            "fuel-wildfires-europe-ocean-surface-temperatures-reach-record"
        ),
    ),
    arctic_sea_ice_context=CuratedClimateContext(
        indicator="arctic_sea_ice_extent",
        headline="Arctic sea-ice extent ranked sixth lowest for July.",
        summary=(
            "Monthly Arctic extent was below its July average, with especially low "
            "cover in parts of the northern Barents Sea."
        ),
        rank=6,
        rank_qualifier="lowest",
        source_url="https://climate.copernicus.eu/sea-ice-cover-july-2026",
    ),
    antarctic_sea_ice_context=CuratedClimateContext(
        indicator="antarctic_sea_ice_extent",
        headline="Antarctic sea-ice extent ranked fifth lowest for July.",
        summary=(
            "Monthly Antarctic extent was below average across most ocean sectors, "
            "with the Amundsen Sea an exception."
        ),
        rank=5,
        rank_qualifier="lowest",
        source_url="https://climate.copernicus.eu/sea-ice-cover-july-2026",
    ),
    precipitation_extremes_note=(
        "Copernicus also reported extensive dry conditions and exceptional wildfire "
        "activity in parts of Europe during the reference month."
    ),
)


CLIMATE_BULLETINS = (COPERNICUS_JULY_2026,)


def select_latest_climate_bulletin(
    bulletins: tuple[CuratedClimateBulletin, ...] = CLIMATE_BULLETINS,
) -> CuratedClimateBulletin:
    if not bulletins:
        raise ValueError("At least one verified climate bulletin is required")
    return max(bulletins, key=lambda item: (item.issue_date, item.verified_at))
