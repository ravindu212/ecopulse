from datetime import datetime

from app.schemas.climate import ClimateDataType, ClimateFreshness, SourceMetadata


NOAA_GML_CO2_SOURCE_NAME = "NOAA GML Estimated Global Trend daily CO2"
NOAA_GML_CO2_PUBLISHER = "NOAA Global Monitoring Laboratory"
NOAA_GML_CO2_METHODOLOGY = (
    "Estimated global atmospheric CO2 trend derived from daily mean observations at "
    "NOAA GML's four atmospheric baseline observatories. Recent values may be "
    "preliminary and subject to revision."
)

EONET_SOURCE_NAME = "NASA Earth Observatory Natural Event Tracker (EONET) v3"
EONET_PUBLISHER = "NASA Earth Science Data Systems"
EONET_METHODOLOGY = (
    "EONET is a curated feed of natural-event metadata assembled from the linked "
    "source organizations; feed inclusion is not climate attribution."
)
NOAA_CPC_ENSO_OBSERVATIONS_NAME = "Weekly OISST.v2.1 Niño-region SST indices"
NOAA_CPC_PUBLISHER = "NOAA Climate Prediction Center"
NOAA_CPC_ENSO_BASELINE = "1991-2020 weekly climatological means"
NOAA_CPC_ENSO_METHODOLOGY = (
    "Weekly area-averaged OISST.v2.1 sea-surface temperature anomalies for the "
    "standard Niño regions. The period date is the CPC week-center date. EcoPulse "
    "reports the SSTA columns, not absolute SST."
)
NOAA_CPC_BULLETIN_METHODOLOGY = (
    "Versioned EcoPulse summary of an issued NOAA CPC ENSO Diagnostic Discussion; "
    "it is authoritative issued analysis, not a live observation feed."
)
WMO_BULLETIN_METHODOLOGY = (
    "Versioned EcoPulse summary of an issued WMO El Niño/La Niña Update; it is "
    "authoritative issued analysis and outlook, not an EcoPulse prediction."
)
WMO_GSCU_SOURCE_NAME = "WMO Global Seasonal Climate Update"
WMO_GSCU_PUBLISHER = "World Meteorological Organization"
WMO_GSCU_METHODOLOGY = (
    "Versioned EcoPulse representation of an issued WMO multi-model seasonal "
    "outlook. It describes probabilities for a multi-month period and is not an "
    "observation, deterministic daily forecast, or long-term climate projection."
)
NOAA_NCEI_PUBLISHER = "NOAA National Centers for Environmental Information"
NOAA_GLOBALTEMP_SOURCE_NAME = (
    "NOAAGlobalTemp v6.1.0 monthly global merged land-ocean anomaly"
)
NOAA_GLOBALTEMP_BASELINE = "1991-2020 monthly climatology"
NOAA_GLOBALTEMP_VERSION = "6.1.0"
NOAA_GLOBALTEMP_METHODOLOGY = (
    "Monthly global merged land-ocean surface temperature anomaly from "
    "NOAAGlobalTemp v6.1.0. The source reports anomaly intervals in kelvin; "
    "EcoPulse expresses the numerically equivalent temperature difference as "
    "degrees Celsius anomaly."
)
COPERNICUS_PUBLISHER = "Copernicus Climate Change Service"
COPERNICUS_BULLETIN_METHODOLOGY = (
    "Versioned EcoPulse summary of an issued Copernicus monthly Climate Bulletin, "
    "primarily based on ERA5 and the cited sea-ice dataset. It is monthly analysis, "
    "not a live sensor feed or forecast."
)
WMO_STATE_OF_GLOBAL_CLIMATE_URL = (
    "https://wmo.int/publication-series/state-of-global-climate"
)
EARTH_EVENT_ATTRIBUTION_DISCLAIMER = (
    "An event's presence in this feed does not establish that climate change caused it. "
    "Attribution requires separate scientific analysis."
)


def noaa_source(
    source_url: str,
    freshness: ClimateFreshness,
    fetched_at: datetime,
    observed_at: datetime | None = None,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=NOAA_GML_CO2_SOURCE_NAME,
        source_url=source_url,
        publisher=NOAA_GML_CO2_PUBLISHER,
        data_type=ClimateDataType.estimate,
        observed_at=observed_at,
        fetched_at=fetched_at,
        freshness=freshness,
        methodology_note=NOAA_GML_CO2_METHODOLOGY,
    )


def eonet_source(
    source_url: str,
    freshness: ClimateFreshness,
    fetched_at: datetime,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=EONET_SOURCE_NAME,
        source_url=source_url,
        publisher=EONET_PUBLISHER,
        data_type=ClimateDataType.observation,
        fetched_at=fetched_at,
        freshness=freshness,
        methodology_note=EONET_METHODOLOGY,
    )


def cpc_enso_observation_source(
    source_url: str,
    freshness: ClimateFreshness,
    fetched_at: datetime,
    observed_at: datetime | None = None,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=NOAA_CPC_ENSO_OBSERVATIONS_NAME,
        source_url=source_url,
        publisher=NOAA_CPC_PUBLISHER,
        data_type=ClimateDataType.observation,
        observed_at=observed_at,
        fetched_at=fetched_at,
        freshness=freshness,
        methodology_note=NOAA_CPC_ENSO_METHODOLOGY,
        baseline=NOAA_CPC_ENSO_BASELINE,
    )


def issued_enso_source(
    *,
    source_name: str,
    source_url: str,
    publisher: str,
    data_type: ClimateDataType,
    published_at: datetime,
    methodology_note: str,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=source_name,
        source_url=source_url,
        publisher=publisher,
        data_type=data_type,
        published_at=published_at,
        freshness=ClimateFreshness.current,
        methodology_note=methodology_note,
    )


def noaa_global_temperature_source(
    source_url: str,
    freshness: ClimateFreshness,
    fetched_at: datetime,
    observed_at: datetime | None = None,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=NOAA_GLOBALTEMP_SOURCE_NAME,
        source_url=source_url,
        publisher=NOAA_NCEI_PUBLISHER,
        data_type=ClimateDataType.analysis,
        observed_at=observed_at,
        fetched_at=fetched_at,
        freshness=freshness,
        methodology_note=NOAA_GLOBALTEMP_METHODOLOGY,
        baseline=NOAA_GLOBALTEMP_BASELINE,
    )


def copernicus_bulletin_source(
    source_name: str,
    source_url: str,
    published_at: datetime,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=source_name,
        source_url=source_url,
        publisher=COPERNICUS_PUBLISHER,
        data_type=ClimateDataType.analysis,
        published_at=published_at,
        freshness=ClimateFreshness.current,
        methodology_note=COPERNICUS_BULLETIN_METHODOLOGY,
    )


def wmo_seasonal_outlook_source(
    *,
    source_url: str,
    published_at: datetime,
    freshness: ClimateFreshness,
    baseline: str,
) -> SourceMetadata:
    return SourceMetadata(
        source_name=WMO_GSCU_SOURCE_NAME,
        source_url=source_url,
        publisher=WMO_GSCU_PUBLISHER,
        data_type=ClimateDataType.forecast,
        published_at=published_at,
        freshness=freshness,
        methodology_note=WMO_GSCU_METHODOLOGY,
        baseline=baseline,
    )
