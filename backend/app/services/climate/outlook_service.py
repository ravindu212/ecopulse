from collections.abc import Callable
from datetime import date, datetime, time, timezone

from app.schemas.climate import (
    ClimateDataType,
    ClimateFreshness,
    ForecastPeriod,
    ProbabilityQualifier,
    SeasonalDriverPhase,
    SeasonalOceanDriver,
    SeasonalOceanicDrivers,
    SeasonalOutlookIssue,
    SeasonalOutlookMethodology,
    SeasonalOutlookPreview,
    SeasonalOutlookResponse,
    SeasonalOutlookSection,
    SeasonalOutlookValidity,
    SeasonalProbability,
    SeasonalTercileCategory,
)
from app.services.climate.cache import utc_now
from app.services.climate.curated.seasonal_outlooks import (
    SEASONAL_OUTLOOKS,
    CuratedOceanDriver,
    CuratedOutlookSection,
    CuratedSeasonalOutlook,
)
from app.services.climate.source_registry import (
    WMO_GSCU_METHODOLOGY,
    wmo_seasonal_outlook_source,
)


OUTLOOK_MEANING = (
    "Seasonal climate outlooks describe shifts in the probability of conditions "
    "over a multi-month period. They do not predict exact weather on a particular day."
)
TERCILE_EXPLANATION = (
    "Seasonal means are commonly grouped into above-normal, near-normal, and "
    "below-normal thirds relative to a stated reference period. A favoured category "
    "does not mean every day will have that condition."
)
DRIVER_INTERACTION_NOTE = (
    "El Niño can shift the likelihood of temperature and rainfall patterns. Other "
    "climate drivers may reinforce, weaken, or alter typical El Niño impacts."
)


class SeasonalOutlookUnavailableError(LookupError):
    pass


def determine_outlook_validity(
    record: CuratedSeasonalOutlook, as_of: date
) -> SeasonalOutlookValidity:
    if as_of < record.forecast_period.start_date:
        return SeasonalOutlookValidity.upcoming
    if as_of > record.forecast_period.end_date:
        return SeasonalOutlookValidity.expired
    return SeasonalOutlookValidity.current


def select_seasonal_outlook(
    records: tuple[CuratedSeasonalOutlook, ...], as_of: date
) -> CuratedSeasonalOutlook:
    verified = [record for record in records if record.verified_at <= as_of]
    if not verified:
        raise SeasonalOutlookUnavailableError(
            "No seasonal outlook has been verified as of the requested date"
        )
    priority = {
        SeasonalOutlookValidity.current: 2,
        SeasonalOutlookValidity.upcoming: 1,
        SeasonalOutlookValidity.expired: 0,
    }
    return max(
        verified,
        key=lambda record: (
            priority[determine_outlook_validity(record, as_of)],
            record.issue_date,
            record.verified_at,
        ),
    )


def _published_at(record: CuratedSeasonalOutlook) -> datetime:
    return datetime.combine(record.issue_date, time.min, tzinfo=timezone.utc)


def _build_driver(driver: CuratedOceanDriver, source) -> SeasonalOceanDriver:
    return SeasonalOceanDriver(
        name=driver.name,
        phase=SeasonalDriverPhase(driver.phase),
        status=driver.status,
        forecast_value=driver.forecast_value,
        unit=driver.unit,
        valid_period=driver.valid_period,
        confidence=driver.confidence,
        source=source,
        methodology_note=driver.methodology_note,
    )


def _build_section(
    section: CuratedOutlookSection,
    record: CuratedSeasonalOutlook,
    source,
) -> SeasonalOutlookSection:
    return SeasonalOutlookSection(
        headline=section.headline,
        narrative=section.narrative,
        forecast_period=record.forecast_period.label,
        baseline=record.baseline,
        tendencies=[
            SeasonalProbability(
                category=SeasonalTercileCategory(item.category),
                probability=item.probability,
                qualifier=ProbabilityQualifier(item.qualifier),
                valid_period=item.valid_period,
                region=item.region,
                source=source,
            )
            for item in section.tendencies
        ],
        source=source,
    )


class SeasonalOutlookService:
    def __init__(
        self,
        records: tuple[CuratedSeasonalOutlook, ...] = SEASONAL_OUTLOOKS,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._records = records
        self._clock = clock

    def get_outlook(self) -> SeasonalOutlookResponse:
        as_of = self._clock().date()
        record = select_seasonal_outlook(self._records, as_of)
        validity = determine_outlook_validity(record, as_of)
        latest = max(
            (item for item in self._records if item.verified_at <= as_of),
            key=lambda item: (item.issue_date, item.verified_at),
        )
        source = wmo_seasonal_outlook_source(
            source_url=record.source_url,
            published_at=_published_at(record),
            freshness=(
                ClimateFreshness.stale
                if validity == SeasonalOutlookValidity.expired
                else ClimateFreshness.current
            ),
            baseline=record.baseline,
        )
        return SeasonalOutlookResponse(
            issue=SeasonalOutlookIssue(
                publisher=record.publisher,
                issue_date=record.issue_date,
                verified_at=record.verified_at,
                source_url=record.source_url,
                data_type=ClimateDataType.forecast,
                latest_known_issue=record == latest,
            ),
            forecast_period=ForecastPeriod(
                label=record.forecast_period.label,
                start_date=record.forecast_period.start_date,
                end_date=record.forecast_period.end_date,
                validity=validity,
            ),
            baseline=record.baseline,
            oceanic_drivers=SeasonalOceanicDrivers(
                enso=_build_driver(record.enso, source),
                iod=_build_driver(record.iod, source) if record.iod else None,
                tropical_atlantic=[
                    _build_driver(driver, source)
                    for driver in record.tropical_atlantic
                ],
            ),
            temperature=_build_section(record.temperature_outlook, record, source),
            precipitation=_build_section(
                record.precipitation_outlook, record, source
            ),
            key_messages=list(record.key_messages),
            methodology=SeasonalOutlookMethodology(
                multi_model_method=record.methodology_note,
                outlook_meaning=OUTLOOK_MEANING,
                tercile_explanation=TERCILE_EXPLANATION,
                driver_interaction_note=DRIVER_INTERACTION_NOTE,
            ),
            limitations=list(record.limitations),
            sources=[source],
        )

    def get_preview(
        self, outlook: SeasonalOutlookResponse | None = None
    ) -> SeasonalOutlookPreview:
        outlook = outlook or self.get_outlook()
        iod = outlook.oceanic_drivers.iod
        driver_summary = outlook.oceanic_drivers.enso.status
        if iod is not None:
            driver_summary = f"{driver_summary} {iod.status}"
        return SeasonalOutlookPreview(
            period=outlook.forecast_period.label,
            headline=outlook.temperature.headline,
            issue_date=outlook.issue.issue_date,
            key_driver_summary=driver_summary,
            validity=outlook.forecast_period.validity,
        )
