from fastapi import APIRouter

from app.api.routes import assessment_router, auth_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(assessment_router)
