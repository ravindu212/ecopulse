import math
from datetime import datetime, timezone

from app.schemas.climate import TemperatureAnomalyPoint
from app.services.climate.co2_service import ClimateDataParseError


def parse_noaa_global_temperature(
    content: str,
    history_limit: int,
) -> list[TemperatureAnomalyPoint]:
    points_by_period: dict[datetime, TemperatureAnomalyPoint] = {}
    for line in content.splitlines():
        columns = line.split()
        if len(columns) < 3:
            continue
        try:
            year = int(columns[0])
            month = int(columns[1])
            anomaly = float(columns[2])
            observed_at = datetime(year, month, 1, tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(anomaly) or anomaly <= -900 or not -20 <= anomaly <= 20:
            continue
        points_by_period[observed_at] = TemperatureAnomalyPoint(
            value=anomaly,
            unit="°C anomaly",
            period=observed_at.strftime("%B %Y"),
            observed_at=observed_at,
        )

    ordered = sorted(points_by_period.values(), key=lambda point: point.observed_at)
    if not ordered:
        raise ClimateDataParseError(
            "NOAA NCEI response contained no valid global temperature observations"
        )
    bounded_limit = max(1, min(history_limit, 60))
    return ordered[-bounded_limit:]
