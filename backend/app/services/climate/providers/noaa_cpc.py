import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from app.schemas.climate import ENSORegion
from app.services.climate.co2_service import ClimateDataParseError


REGION_ORDER = (
    ENSORegion.nino_1_2,
    ENSORegion.nino_3,
    ENSORegion.nino_3_4,
    ENSORegion.nino_4,
)
NUMBER_PATTERN = re.compile(r"[+-]?\d+(?:\.\d+)?")


@dataclass(frozen=True)
class CPCWeeklyENSORecord:
    observed_at: datetime
    anomalies: dict[ENSORegion, float]


def parse_cpc_weekly_enso(content: str) -> list[CPCWeeklyENSORecord]:
    """Parse CPC weekly SST/SSTA pairs, returning anomaly values only."""
    records_by_date: dict[datetime, CPCWeeklyENSORecord] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or not re.match(r"^\d{2}[A-Za-z]{3}\d{4}", stripped):
            continue
        try:
            observed_at = datetime.strptime(stripped[:9], "%d%b%Y").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue

        values = [float(value) for value in NUMBER_PATTERN.findall(stripped[9:])]
        if len(values) != 8 or not all(math.isfinite(value) for value in values):
            continue
        absolute_sst = values[0::2]
        anomalies = values[1::2]
        if not all(-5 <= value <= 40 for value in absolute_sst):
            continue
        if not all(-10 <= value <= 10 for value in anomalies):
            continue
        records_by_date[observed_at] = CPCWeeklyENSORecord(
            observed_at=observed_at,
            anomalies=dict(zip(REGION_ORDER, anomalies, strict=True)),
        )

    records = sorted(records_by_date.values(), key=lambda record: record.observed_at)
    if not records:
        raise ClimateDataParseError("CPC response contained no valid ENSO observations")
    return records
