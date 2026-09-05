from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CuratedProbability:
    label: str
    probability: float | None
    qualifier: str | None
    valid_period: str


@dataclass(frozen=True)
class CuratedENSOBulletin:
    source_name: str
    publisher: str
    issue_date: date
    source_url: str
    verified_at: date
    alert_status: str | None
    headline: str
    summary: str
    valid_period: str | None
    probabilities: tuple[CuratedProbability, ...]


NOAA_CPC_BULLETIN = CuratedENSOBulletin(
    source_name="NOAA CPC ENSO Diagnostic Discussion - August 2026",
    publisher="NOAA Climate Prediction Center",
    issue_date=date(2026, 8, 13),
    source_url=(
        "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/"
        "enso_disc_aug2026/ensodisc.shtml"
    ),
    verified_at=date(2026, 9, 5),
    alert_status="El Niño Advisory",
    headline="El Niño is strengthening.",
    summary=(
        "NOAA CPC reported coupled ocean-atmosphere conditions consistent with a "
        "strengthening El Niño and emphasized that expected impacts are not guaranteed."
    ),
    valid_period="Northern Hemisphere fall and winter 2026-27",
    probabilities=(
        CuratedProbability(
            label="Very strong El Niño event",
            probability=90,
            qualifier="greater_than",
            valid_period="Northern Hemisphere fall and winter 2026-27",
        ),
        CuratedProbability(
            label="Historic event exceeding earlier events in the record since 1950",
            probability=69,
            qualifier="exact",
            valid_period="October-December 2026",
        ),
    ),
)


WMO_BULLETIN = CuratedENSOBulletin(
    source_name="WMO El Niño/La Niña Update - August 2026",
    publisher="World Meteorological Organization",
    issue_date=date(2026, 9, 3),
    source_url=(
        "https://wmo.int/resources/publication-series/el-ninola-nina-updates/"
        "august-2026"
    ),
    verified_at=date(2026, 9, 5),
    alert_status=None,
    headline="El Niño is firmly established and expected to strengthen further.",
    summary=(
        "WMO reported persistent tropical Pacific warming and an outlook for further "
        "strengthening, while cautioning that event strength does not determine the "
        "magnitude of impacts in a particular region."
    ),
    valid_period="September 2026-February 2027",
    probabilities=(
        CuratedProbability(
            label="El Niño persists",
            probability=100,
            qualifier="near",
            valid_period=(
                "September-November 2026 and December 2026-February 2027"
            ),
        ),
    ),
)
