from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CuratedForecastPeriod:
    label: str
    start_date: date
    end_date: date

    def __post_init__(self):
        if self.end_date < self.start_date:
            raise ValueError("Forecast period end date cannot precede its start date")


@dataclass(frozen=True)
class CuratedSeasonalProbability:
    category: str
    probability: float | None
    qualifier: str
    valid_period: str
    region: str

    def __post_init__(self):
        if self.probability is not None and not 0 <= self.probability <= 100:
            raise ValueError("Seasonal probability must be between 0 and 100")


@dataclass(frozen=True)
class CuratedOceanDriver:
    name: str
    phase: str
    status: str
    forecast_value: float | None
    unit: str | None
    valid_period: str
    confidence: str | None = None
    methodology_note: str = "Source-attributed WMO multi-model ensemble forecast."


@dataclass(frozen=True)
class CuratedOutlookSection:
    headline: str
    narrative: str
    tendencies: tuple[CuratedSeasonalProbability, ...]


@dataclass(frozen=True)
class CuratedSeasonalOutlook:
    source_name: str
    publisher: str
    issue_date: date
    verified_at: date
    source_url: str
    forecast_period: CuratedForecastPeriod
    baseline: str
    enso: CuratedOceanDriver
    iod: CuratedOceanDriver | None
    tropical_atlantic: tuple[CuratedOceanDriver, ...]
    temperature_outlook: CuratedOutlookSection
    precipitation_outlook: CuratedOutlookSection
    key_messages: tuple[str, ...]
    methodology_note: str
    limitations: tuple[str, ...]


WMO_GSCU_SON_2026 = CuratedSeasonalOutlook(
    source_name=(
        "WMO Global Seasonal Climate Update - September-October-November 2026"
    ),
    publisher="World Meteorological Organization",
    issue_date=date(2026, 9, 3),
    verified_at=date(2026, 9, 5),
    source_url=(
        "https://wmo.int/resources/publication-series/global-seasonal-climate-"
        "updates/gscu-son2026"
    ),
    forecast_period=CuratedForecastPeriod(
        label="September-November 2026",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 11, 30),
    ),
    baseline="1993-2009",
    enso=CuratedOceanDriver(
        name="ENSO / Niño 3.4",
        phase="el_nino",
        status=(
            "El Niño conditions are forecast to strengthen further, with the "
            "intensification trajectory peaking around November-December."
        ),
        forecast_value=3.6,
        unit="°C SST anomaly",
        valid_period="September-November 2026 seasonal mean",
        confidence="High confidence; individual forecast systems have a narrow spread.",
    ),
    iod=CuratedOceanDriver(
        name="Indian Ocean Dipole",
        phase="positive",
        status="A positive Indian Ocean Dipole phase is expected to develop.",
        forecast_value=0.9,
        unit="°C index anomaly",
        valid_period="September-November 2026 seasonal mean",
    ),
    tropical_atlantic=(
        CuratedOceanDriver(
            name="North Tropical Atlantic",
            phase="above_normal",
            status="Sea-surface temperatures are forecast to stay above normal.",
            forecast_value=None,
            unit=None,
            valid_period="September-November 2026",
        ),
        CuratedOceanDriver(
            name="South Tropical Atlantic",
            phase="above_normal",
            status="Sea-surface temperatures are forecast to stay above normal.",
            forecast_value=None,
            unit=None,
            valid_period="September-November 2026",
        ),
    ),
    temperature_outlook=CuratedOutlookSection(
        headline="Above-normal seasonal temperatures are favoured across most land areas.",
        narrative=(
            "The WMO multi-model outlook indicates an increased likelihood of "
            "above-normal seasonal-mean temperatures across most of the world's "
            "land areas, with regional exceptions and differing forecast strength."
        ),
        tendencies=(
            CuratedSeasonalProbability(
                category="above_normal",
                probability=None,
                qualifier="not_specified",
                valid_period="September-November 2026",
                region="Most global land areas",
            ),
            CuratedSeasonalProbability(
                category="above_normal",
                probability=80,
                qualifier="greater_than",
                valid_period="September-November 2026",
                region="Equatorial Pacific east of the Date Line",
            ),
        ),
    ),
    precipitation_outlook=CuratedOutlookSection(
        headline="Rainfall probabilities show a pronounced El Niño-related pattern.",
        narrative=(
            "The outlook favours above-normal precipitation across the central and "
            "eastern equatorial Pacific, with increased likelihoods of below-normal "
            "precipitation across several flanking tropical ocean regions."
        ),
        tendencies=(
            CuratedSeasonalProbability(
                category="above_normal",
                probability=None,
                qualifier="not_specified",
                valid_period="September-November 2026",
                region="Central and eastern equatorial Pacific east of the Date Line",
            ),
            CuratedSeasonalProbability(
                category="below_normal",
                probability=None,
                qualifier="not_specified",
                valid_period="September-November 2026",
                region="Tropical Indian Ocean and equatorial Atlantic Ocean",
            ),
        ),
    ),
    key_messages=(
        "El Niño is forecast to strengthen further during the outlook period.",
        "A positive Indian Ocean Dipole is expected to develop.",
        "Above-normal seasonal temperatures are favoured across most land areas.",
        "Rainfall probabilities display a strong El Niño-related spatial pattern.",
    ),
    methodology_note=(
        "WMO combines forecasts from Global Producing Centres in a multi-model "
        "ensemble and expresses temperature and precipitation as probabilities of "
        "seasonal means falling into tercile categories relative to local climatology."
    ),
    limitations=(
        "This global seasonal outlook is broad-scale guidance, not a daily or local "
        "weather forecast.",
        "A favoured tercile is not certain and does not mean every day will share that "
        "condition.",
        "Regional and national outlooks from WMO Regional Climate Centres and National "
        "Meteorological and Hydrological Services should guide local decisions.",
        "El Niño can shift temperature and rainfall probabilities, while other drivers "
        "can reinforce, weaken, or alter typical impacts.",
    ),
)


SEASONAL_OUTLOOKS = (WMO_GSCU_SON_2026,)
