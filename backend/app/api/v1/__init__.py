from fastapi import APIRouter

from app.api.routes import auth_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
