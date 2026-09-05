from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.schemas.climate import CO2Response, EarthEventsResponse
from app.services.climate import CO2Service, EarthEventsService


router = APIRouter(prefix="/climate", tags=["climate"])

_co2_service = CO2Service()
_events_service = EarthEventsService()


def get_co2_service() -> CO2Service:
    return _co2_service


def get_events_service() -> EarthEventsService:
    return _events_service


@router.get("/co2", response_model=CO2Response)
def climate_co2(service: Annotated[CO2Service, Depends(get_co2_service)]):
    return service.get_co2()


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
