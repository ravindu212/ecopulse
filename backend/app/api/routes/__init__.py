from app.api.routes.assessment import router as assessment_router
from app.api.routes.actions import router as actions_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.auth import router as auth_router
from app.api.routes.challenges import router as challenges_router

__all__ = ["actions_router", "assessment_router", "auth_router", "challenges_router", "dashboard_router"]
