import csv
import io
import logging
import math
from collections.abc import Callable
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.climate import (
    CO2Response,
    ClimateFreshness,
    ClimateNumericDatum,
    ClimateSeriesPoint,
)
from app.services.climate.cache import TTLCache, utc_now
from app.services.climate.http_client import ProviderHttpClient, ProviderRequestError
from app.services.climate.source_registry import NOAA_GML_CO2_METHODOLOGY, noaa_source


logger = logging.getLogger(__name__)
CO2_CACHE_KEY = "noaa-global-daily-trend"


class ClimateDataParseError(ValueError):
    pass


def parse_noaa_global_trend_csv(
    content: str,
    history_limit: int,
) -> list[ClimateSeriesPoint]:
    data_lines = [
        line
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not data_lines:
        raise ClimateDataParseError("NOAA response contained no data rows")

    reader = csv.DictReader(io.StringIO("\n".join(data_lines)))
    required = {"year", "month", "day", "trend"}
    if reader.fieldnames is None or not required.issubset(
        {name.strip().lower() for name in reader.fieldnames}
    ):
        raise ClimateDataParseError("NOAA response columns were not recognized")

    points_by_date: dict[datetime, ClimateSeriesPoint] = {}
    for raw_row in reader:
        row = {
            (key or "").strip().lower(): (value or "").strip()
            for key, value in raw_row.items()
        }
        try:
            observed_at = datetime(
                int(row["year"]),
                int(row["month"]),
                int(row["day"]),
                tzinfo=timezone.utc,
            )
            value = float(row["trend"])
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(value) or value <= 0:
            continue
        points_by_date[observed_at] = ClimateSeriesPoint(
            value=value,
            unit="ppm",
            observed_at=observed_at,
        )

    ordered = sorted(points_by_date.values(), key=lambda point: point.observed_at)
    if not ordered:
        raise ClimateDataParseError("NOAA response contained no valid observations")
    return ordered[-history_limit:]


class CO2Service:
    def __init__(
        self,
        http_client: ProviderHttpClient | None = None,
        cache: TTLCache[CO2Response] | None = None,
        source_url: str = settings.climate_co2_url,
        ttl_seconds: int = settings.climate_co2_ttl_seconds,
        history_limit: int = settings.climate_co2_history_limit,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._http = http_client or ProviderHttpClient()
        self._cache = cache or TTLCache(clock=clock)
        self._source_url = source_url
        self._ttl_seconds = ttl_seconds
        self._history_limit = history_limit
        self._clock = clock

    def get_co2(self) -> CO2Response:
        cached = self._cache.get_fresh(CO2_CACHE_KEY)
        if cached is not None:
            return cached.value

        try:
            content = self._http.get_text(self._source_url)
            series = parse_noaa_global_trend_csv(content, self._history_limit)
            fetched_at = self._clock()
            latest_point = series[-1]
            source = noaa_source(
                self._source_url,
                ClimateFreshness.current,
                fetched_at,
                latest_point.observed_at,
            )
            response = CO2Response(
                latest=ClimateNumericDatum(
                    label="Estimated global atmospheric CO2 trend",
                    value=latest_point.value,
                    unit="ppm",
                    observed_at=latest_point.observed_at,
                    source=source,
                    methodology_note=NOAA_GML_CO2_METHODOLOGY,
                ),
                series=series,
                source=source,
                status=ClimateFreshness.current,
            )
            self._cache.put(CO2_CACHE_KEY, response, self._ttl_seconds)
            return response
        except (ProviderRequestError, ClimateDataParseError, TypeError, ValueError) as exc:
            logger.warning("NOAA GML CO2 refresh failed: %s", type(exc).__name__)
            stale = self._cache.get_last_known_good(CO2_CACHE_KEY)
            if stale is not None:
                return self._as_stale(stale.value)
            fetched_at = self._clock()
            return CO2Response(
                latest=None,
                series=[],
                source=noaa_source(
                    self._source_url,
                    ClimateFreshness.unavailable,
                    fetched_at,
                ),
                status=ClimateFreshness.unavailable,
            )

    @staticmethod
    def _as_stale(response: CO2Response) -> CO2Response:
        source = response.source.model_copy(update={"freshness": ClimateFreshness.stale})
        latest = response.latest
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
                "latest": latest,
                "source": source,
                "status": ClimateFreshness.stale,
            }
        )
