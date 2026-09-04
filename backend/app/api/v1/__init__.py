from fastapi import APIRouter

from app.api.routes import actions_router, assessment_router, auth_router, dashboard_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(assessment_router)
api_router.include_router(actions_router)
api_router.include_router(dashboard_router)
