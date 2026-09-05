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
