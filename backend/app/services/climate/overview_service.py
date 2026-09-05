from collections.abc import Callable
from datetime import datetime

from app.schemas.climate import (
    CO2Overview,
    ClimateAvailability,
    ClimateFreshness,
    ClimateOverviewResponse,
    ENSOOverview,
    EarthEventsOverview,
    SeaIceOverview,
    SeasonalOutlookPreview,
    SourceMetadata,
)
from app.services.climate.bulletin_service import ClimateBulletinService
from app.services.climate.cache import utc_now
from app.services.climate.co2_service import CO2Service
from app.services.climate.enso_service import ENSOService
from app.services.climate.events_service import EarthEventsService
from app.services.climate.outlook_service import (
    SeasonalOutlookService,
    SeasonalOutlookUnavailableError,
)
from app.services.climate.temperature_service import GlobalTemperatureService


def _classify_availability(
    component_freshness: dict[str, ClimateFreshness],
) -> ClimateAvailability:
    available = []
    stale = []
    unavailable = []
    for component, freshness in component_freshness.items():
        if freshness in {ClimateFreshness.live, ClimateFreshness.current}:
            available.append(component)
        elif freshness == ClimateFreshness.stale:
            stale.append(component)
        else:
            unavailable.append(component)
    return ClimateAvailability(
        available_components=available,
        stale_components=stale,
        unavailable_components=unavailable,
    )


def _unique_sources(sources: list[SourceMetadata]) -> list[SourceMetadata]:
    unique: dict[tuple[str, str, str], SourceMetadata] = {}
    for source in sources:
        key = (source.publisher, source.source_url, source.data_type.value)
        unique[key] = source
    return list(unique.values())


class ClimateOverviewService:
    def __init__(
        self,
        co2_service: CO2Service | None = None,
        enso_service: ENSOService | None = None,
        temperature_service: GlobalTemperatureService | None = None,
        events_service: EarthEventsService | None = None,
        bulletin_service: ClimateBulletinService | None = None,
        outlook_service: SeasonalOutlookService | None = None,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._co2 = co2_service or CO2Service()
        self._enso = enso_service or ENSOService()
        self._temperature = temperature_service or GlobalTemperatureService()
        self._events = events_service or EarthEventsService()
        self._bulletins = bulletin_service or ClimateBulletinService()
        self._outlook = outlook_service or SeasonalOutlookService()
        self._clock = clock

    def get_overview(self) -> ClimateOverviewResponse:
        co2 = self._co2.get_co2()
        enso = self._enso.get_enso()
        temperature = self._temperature.get_global_temperature()
        events = self._events.get_events(days=30, limit=10)
        bulletin = self._bulletins.get_latest()
        seasonal_outlook: SeasonalOutlookPreview | None = None
        seasonal_outlook_source: SourceMetadata | None = None
        seasonal_outlook_freshness = ClimateFreshness.unavailable
        try:
            full_outlook = self._outlook.get_outlook()
            seasonal_outlook = self._outlook.get_preview(full_outlook)
            seasonal_outlook_source = full_outlook.sources[0]
            seasonal_outlook_freshness = seasonal_outlook_source.freshness
        except SeasonalOutlookUnavailableError:
            pass

        availability = _classify_availability(
            {
                "co2": co2.status,
                "enso_observations": enso.observation_freshness,
                "enso_analysis": ClimateFreshness.current,
                "global_temperature": temperature.freshness,
                "ocean_analysis": ClimateFreshness.current,
                "arctic_sea_ice_analysis": ClimateFreshness.current,
                "antarctic_sea_ice_analysis": ClimateFreshness.current,
                "earth_events": events.freshness,
                "climate_bulletin": ClimateFreshness.current,
                "seasonal_outlook": seasonal_outlook_freshness,
            }
        )
        sources = _unique_sources(
            [
                co2.source,
                *enso.sources,
                temperature.source,
                events.source,
                bulletin.source,
                bulletin.temperature_context.source,
                bulletin.sea_surface_temperature_context.source,
                bulletin.arctic_sea_ice_context.source,
                bulletin.antarctic_sea_ice_context.source,
                *([seasonal_outlook_source] if seasonal_outlook_source else []),
            ]
        )
        return ClimateOverviewResponse(
            generated_at=self._clock(),
            co2=CO2Overview(
                latest=co2.latest,
                freshness=co2.status,
                source=co2.source,
            ),
            enso=ENSOOverview(
                status=enso.status,
                latest_nino34=enso.observations.latest_nino34,
                observation_freshness=enso.observation_freshness,
                observation_source=enso.observations.source,
            ),
            global_temperature=temperature,
            ocean=bulletin.sea_surface_temperature_context,
            sea_ice=SeaIceOverview(
                arctic=bulletin.arctic_sea_ice_context,
                antarctic=bulletin.antarctic_sea_ice_context,
            ),
            earth_events=EarthEventsOverview(
                returned_event_count=events.count,
                window_days=30,
                result_limit=10,
                freshness=events.freshness,
                source=events.source,
                attribution_disclaimer=events.attribution_disclaimer,
            ),
            latest_bulletin=bulletin,
            seasonal_outlook=seasonal_outlook,
            sources=sources,
            availability=availability,
        )
