import logging
from collections.abc import Callable
from datetime import date, datetime, time, timezone

from app.core.config import settings
from app.schemas.climate import (
    ClimateDataType,
    ClimateFreshness,
    ENSOIssuedOutlook,
    ENSOObservation,
    ENSOObservations,
    ENSOOutlook,
    ENSOPhase,
    ENSOProbability,
    ENSORegion,
    ENSOResponse,
    ENSOStatus,
    ProbabilityQualifier,
    SourceMetadata,
)
from app.services.climate.cache import TTLCache, utc_now
from app.services.climate.co2_service import ClimateDataParseError
from app.services.climate.curated import NOAA_CPC_BULLETIN, WMO_BULLETIN
from app.services.climate.curated.enso_bulletins import CuratedENSOBulletin
from app.services.climate.http_client import ProviderHttpClient, ProviderRequestError
from app.services.climate.providers import CPCWeeklyENSORecord, parse_cpc_weekly_enso
from app.services.climate.source_registry import (
    NOAA_CPC_BULLETIN_METHODOLOGY,
    NOAA_CPC_ENSO_METHODOLOGY,
    WMO_BULLETIN_METHODOLOGY,
    cpc_enso_observation_source,
    issued_enso_source,
)


logger = logging.getLogger(__name__)
ENSO_CACHE_KEY = "noaa-cpc-weekly-nino-regions"
REGION_NAMES = {
    ENSORegion.nino_1_2: "Niño 1+2",
    ENSORegion.nino_3: "Niño 3",
    ENSORegion.nino_3_4: "Niño 3.4",
    ENSORegion.nino_4: "Niño 4",
}
ENSO_EXPLANATORY_NOTES = [
    (
        "ENSO is a coupled ocean-atmosphere pattern in the tropical Pacific; the "
        "weekly Niño observations here are ocean temperature anomalies, not forecasts."
    ),
    (
        "ENSO can shift the probabilities of temperature and rainfall patterns, but "
        "event strength alone does not determine impacts in a particular region."
    ),
    (
        "An ENSO outlook describes large-scale climate probabilities and is not a "
        "deterministic daily weather forecast for an individual location."
    ),
]


def normalize_enso_phase(text: str | None) -> ENSOPhase:
    if not text:
        return ENSOPhase.unknown
    normalized = text.casefold().replace("ñ", "n")
    has_el_nino = "el nino advisory" in normalized
    has_la_nina = "la nina advisory" in normalized
    if has_el_nino and has_la_nina:
        return ENSOPhase.unknown
    if has_el_nino:
        return ENSOPhase.el_nino
    if has_la_nina:
        return ENSOPhase.la_nina
    if "enso-neutral" in normalized or "enso neutral" in normalized:
        return ENSOPhase.neutral
    return ENSOPhase.unknown


def _as_midnight_utc(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _build_observation(
    record: CPCWeeklyENSORecord,
    region: ENSORegion,
    source: SourceMetadata,
) -> ENSOObservation:
    observation_source = source.model_copy(
        update={"observed_at": record.observed_at}
    )
    return ENSOObservation(
        region=region,
        region_name=REGION_NAMES[region],
        value=record.anomalies[region],
        unit="°C anomaly",
        period=f"Week centered on {record.observed_at.date().isoformat()}",
        observed_at=record.observed_at,
        source=observation_source,
        methodology_note=NOAA_CPC_ENSO_METHODOLOGY,
    )


def _build_outlook(
    bulletin: CuratedENSOBulletin,
    source_name: str,
    methodology_note: str,
) -> ENSOIssuedOutlook:
    published_at = _as_midnight_utc(bulletin.issue_date)
    analysis_source = issued_enso_source(
        source_name=source_name,
        source_url=bulletin.source_url,
        publisher=bulletin.publisher,
        data_type=ClimateDataType.analysis,
        published_at=published_at,
        methodology_note=methodology_note,
    )
    forecast_source = issued_enso_source(
        source_name=f"{source_name} - issued outlook",
        source_url=bulletin.source_url,
        publisher=bulletin.publisher,
        data_type=ClimateDataType.forecast,
        published_at=published_at,
        methodology_note=methodology_note,
    )
    return ENSOIssuedOutlook(
        publisher=bulletin.publisher,
        issue_date=bulletin.issue_date,
        verified_at=bulletin.verified_at,
        headline=bulletin.headline,
        summary=bulletin.summary,
        probabilities=[
            ENSOProbability(
                label=item.label,
                probability=item.probability,
                qualifier=ProbabilityQualifier(item.qualifier)
                if item.qualifier
                else None,
                valid_period=item.valid_period,
                issued_at=bulletin.issue_date,
                source=forecast_source,
            )
            for item in bulletin.probabilities
        ],
        valid_period=bulletin.valid_period,
        source=analysis_source,
        latest_known_issue=True,
        methodology_note=methodology_note,
    )


class ENSOService:
    def __init__(
        self,
        http_client: ProviderHttpClient | None = None,
        cache: TTLCache[ENSOObservations] | None = None,
        source_url: str = settings.climate_enso_observations_url,
        ttl_seconds: int = settings.climate_enso_observations_ttl_seconds,
        history_limit: int = settings.climate_enso_history_limit,
        clock: Callable[[], datetime] = utc_now,
        noaa_bulletin: CuratedENSOBulletin = NOAA_CPC_BULLETIN,
        wmo_bulletin: CuratedENSOBulletin = WMO_BULLETIN,
    ):
        self._http = http_client or ProviderHttpClient()
        self._cache = cache or TTLCache(clock=clock)
        self._source_url = source_url
        self._ttl_seconds = ttl_seconds
        self._history_limit = max(1, min(history_limit, 52))
        self._clock = clock
        self._noaa_bulletin = noaa_bulletin
        self._wmo_bulletin = wmo_bulletin

    def get_enso(self) -> ENSOResponse:
        observations = self._get_observations()
        noaa_outlook = _build_outlook(
            self._noaa_bulletin,
            self._noaa_bulletin.source_name,
            NOAA_CPC_BULLETIN_METHODOLOGY,
        )
        wmo_outlook = _build_outlook(
            self._wmo_bulletin,
            self._wmo_bulletin.source_name,
            WMO_BULLETIN_METHODOLOGY,
        )
        status_source = issued_enso_source(
            source_name=self._noaa_bulletin.source_name,
            source_url=self._noaa_bulletin.source_url,
            publisher=self._noaa_bulletin.publisher,
            data_type=ClimateDataType.analysis,
            published_at=_as_midnight_utc(self._noaa_bulletin.issue_date),
            methodology_note=NOAA_CPC_BULLETIN_METHODOLOGY,
        )
        alert_status = self._noaa_bulletin.alert_status or "Unknown"
        status = ENSOStatus(
            alert_status=alert_status,
            enso_phase=normalize_enso_phase(alert_status),
            headline=self._noaa_bulletin.headline,
            summary=self._noaa_bulletin.summary,
            issued_at=self._noaa_bulletin.issue_date,
            source=status_source,
            latest_known_issue=True,
        )
        return ENSOResponse(
            status=status,
            observations=observations,
            outlook=ENSOOutlook(noaa=noaa_outlook, wmo=wmo_outlook),
            sources=[
                observations.source,
                status_source,
                noaa_outlook.source,
                wmo_outlook.source,
                *(
                    [noaa_outlook.probabilities[0].source]
                    if noaa_outlook.probabilities
                    else []
                ),
                *(
                    [wmo_outlook.probabilities[0].source]
                    if wmo_outlook.probabilities
                    else []
                ),
            ],
            observation_freshness=observations.freshness,
            explanatory_notes=ENSO_EXPLANATORY_NOTES,
        )

    def _get_observations(self) -> ENSOObservations:
        cached = self._cache.get_fresh(ENSO_CACHE_KEY)
        if cached is not None:
            return cached.value

        try:
            records = parse_cpc_weekly_enso(self._http.get_text(self._source_url))
            fetched_at = self._clock()
            latest = records[-1]
            source = cpc_enso_observation_source(
                self._source_url,
                ClimateFreshness.current,
                fetched_at,
                latest.observed_at,
            )
            recent_records = records[-self._history_limit :]
            observations = ENSOObservations(
                latest_nino34=_build_observation(latest, ENSORegion.nino_3_4, source),
                regions=[
                    _build_observation(latest, region, source) for region in REGION_NAMES
                ],
                nino34_series=[
                    _build_observation(record, ENSORegion.nino_3_4, source)
                    for record in recent_records
                ],
                source=source,
                freshness=ClimateFreshness.current,
            )
            self._cache.put(ENSO_CACHE_KEY, observations, self._ttl_seconds)
            return observations
        except (ProviderRequestError, ClimateDataParseError, TypeError, ValueError) as exc:
            logger.warning("NOAA CPC ENSO refresh failed: %s", type(exc).__name__)
            stale = self._cache.get_last_known_good(ENSO_CACHE_KEY)
            if stale is not None:
                return self._as_stale(stale.value)
            return ENSOObservations(
                latest_nino34=None,
                regions=[],
                nino34_series=[],
                source=cpc_enso_observation_source(
                    self._source_url,
                    ClimateFreshness.unavailable,
                    self._clock(),
                ),
                freshness=ClimateFreshness.unavailable,
            )

    @staticmethod
    def _as_stale(observations: ENSOObservations) -> ENSOObservations:
        source = observations.source.model_copy(
            update={"freshness": ClimateFreshness.stale}
        )

        def stale_observation(observation: ENSOObservation) -> ENSOObservation:
            return observation.model_copy(
                update={
                    "source": observation.source.model_copy(
                        update={"freshness": ClimateFreshness.stale}
                    )
                }
            )

        return observations.model_copy(
            update={
                "latest_nino34": stale_observation(observations.latest_nino34)
                if observations.latest_nino34
                else None,
                "regions": [stale_observation(item) for item in observations.regions],
                "nino34_series": [
                    stale_observation(item) for item in observations.nino34_series
                ],
                "source": source,
                "freshness": ClimateFreshness.stale,
            }
        )
