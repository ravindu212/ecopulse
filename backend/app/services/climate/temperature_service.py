import logging
from collections.abc import Callable
from datetime import datetime

from app.core.config import settings
from app.schemas.climate import (
    ClimateFreshness,
    GlobalTemperatureResponse,
    TemperatureAnomaly,
)
from app.services.climate.cache import TTLCache, utc_now
from app.services.climate.co2_service import ClimateDataParseError
from app.services.climate.http_client import ProviderHttpClient, ProviderRequestError
from app.services.climate.providers import parse_noaa_global_temperature
from app.services.climate.source_registry import (
    NOAA_GLOBALTEMP_BASELINE,
    NOAA_GLOBALTEMP_METHODOLOGY,
    NOAA_GLOBALTEMP_VERSION,
    noaa_global_temperature_source,
)


logger = logging.getLogger(__name__)
GLOBAL_TEMPERATURE_CACHE_KEY = "noaa-ncei-global-temperature-monthly"


class GlobalTemperatureService:
    def __init__(
        self,
        http_client: ProviderHttpClient | None = None,
        cache: TTLCache[GlobalTemperatureResponse] | None = None,
        source_url: str = settings.climate_global_temperature_url,
        ttl_seconds: int = settings.climate_global_temperature_ttl_seconds,
        history_limit: int = settings.climate_global_temperature_history_limit,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._http = http_client or ProviderHttpClient()
        self._cache = cache or TTLCache(clock=clock)
        self._source_url = source_url
        self._ttl_seconds = ttl_seconds
        self._history_limit = history_limit
        self._clock = clock

    def get_global_temperature(self) -> GlobalTemperatureResponse:
        cached = self._cache.get_fresh(GLOBAL_TEMPERATURE_CACHE_KEY)
        if cached is not None:
            return cached.value

        try:
            series = parse_noaa_global_temperature(
                self._http.get_text(self._source_url), self._history_limit
            )
            fetched_at = self._clock()
            latest_point = series[-1]
            source = noaa_global_temperature_source(
                self._source_url,
                ClimateFreshness.current,
                fetched_at,
                latest_point.observed_at,
            )
            response = GlobalTemperatureResponse(
                latest_anomaly=TemperatureAnomaly(
                    **latest_point.model_dump(),
                    label="Global merged land-ocean surface temperature anomaly",
                    source=source,
                    methodology_note=NOAA_GLOBALTEMP_METHODOLOGY,
                ),
                historical_series=series,
                baseline=NOAA_GLOBALTEMP_BASELINE,
                product_version=NOAA_GLOBALTEMP_VERSION,
                source=source,
                methodology_note=NOAA_GLOBALTEMP_METHODOLOGY,
                freshness=ClimateFreshness.current,
            )
            self._cache.put(
                GLOBAL_TEMPERATURE_CACHE_KEY, response, self._ttl_seconds
            )
            return response
        except (ProviderRequestError, ClimateDataParseError, TypeError, ValueError) as exc:
            logger.warning(
                "NOAA NCEI global temperature refresh failed: %s", type(exc).__name__
            )
            stale = self._cache.get_last_known_good(GLOBAL_TEMPERATURE_CACHE_KEY)
            if stale is not None:
                return self._as_stale(stale.value)
            return GlobalTemperatureResponse(
                latest_anomaly=None,
                historical_series=[],
                baseline=NOAA_GLOBALTEMP_BASELINE,
                product_version=NOAA_GLOBALTEMP_VERSION,
                source=noaa_global_temperature_source(
                    self._source_url,
                    ClimateFreshness.unavailable,
                    self._clock(),
                ),
                methodology_note=NOAA_GLOBALTEMP_METHODOLOGY,
                freshness=ClimateFreshness.unavailable,
            )

    @staticmethod
    def _as_stale(response: GlobalTemperatureResponse) -> GlobalTemperatureResponse:
        source = response.source.model_copy(
            update={"freshness": ClimateFreshness.stale}
        )
        latest = response.latest_anomaly
        if latest is not None:
            latest = latest.model_copy(
                update={
                    "source": latest.source.model_copy(
                        update={"freshness": ClimateFreshness.stale}
                    )
                }
            )
        return response.model_copy(
            update={
                "latest_anomaly": latest,
                "source": source,
                "freshness": ClimateFreshness.stale,
            }
        )
