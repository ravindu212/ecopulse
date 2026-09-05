from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.climate import (
    CO2Response,
    ClimateOverviewResponse,
    ENSOResponse,
    EarthEventsResponse,
    SeasonalOutlookResponse,
)
from app.services.climate import (
    CO2Service,
    ClimateOverviewService,
    ENSOService,
    EarthEventsService,
    GlobalTemperatureService,
    SeasonalOutlookService,
)
from app.services.climate.outlook_service import SeasonalOutlookUnavailableError


router = APIRouter(prefix="/climate", tags=["climate"])

_co2_service = CO2Service()
_events_service = EarthEventsService()
_enso_service = ENSOService()
_temperature_service = GlobalTemperatureService()
_outlook_service = SeasonalOutlookService()
_overview_service = ClimateOverviewService(
    co2_service=_co2_service,
    enso_service=_enso_service,
    temperature_service=_temperature_service,
    events_service=_events_service,
    outlook_service=_outlook_service,
)


def get_co2_service() -> CO2Service:
    return _co2_service


def get_events_service() -> EarthEventsService:
    return _events_service


def get_enso_service() -> ENSOService:
    return _enso_service


def get_overview_service() -> ClimateOverviewService:
    return _overview_service


def get_outlook_service() -> SeasonalOutlookService:
    return _outlook_service


@router.get("/co2", response_model=CO2Response)
def climate_co2(service: Annotated[CO2Service, Depends(get_co2_service)]):
    return service.get_co2()


@router.get("/enso", response_model=ENSOResponse)
def climate_enso(service: Annotated[ENSOService, Depends(get_enso_service)]):
    return service.get_enso()


@router.get("/overview", response_model=ClimateOverviewResponse)
def climate_overview(
    service: Annotated[ClimateOverviewService, Depends(get_overview_service)],
):
    return service.get_overview()


@router.get("/outlook", response_model=SeasonalOutlookResponse)
def climate_outlook(
    service: Annotated[SeasonalOutlookService, Depends(get_outlook_service)],
):
    try:
        return service.get_outlook()
    except SeasonalOutlookUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No verified seasonal climate outlook is currently available.",
        ) from exc


@router.get("/events", response_model=EarthEventsResponse)
def earth_events(
    service: Annotated[EarthEventsService, Depends(get_events_service)],
    category: Annotated[
        str | None,
        Query(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$"),
    ] = None,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.get_events(category=category, days=days, limit=limit)
