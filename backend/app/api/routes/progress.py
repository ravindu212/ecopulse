from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.progress import ProgressOut
from app.services.progress_service import get_progress


router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=ProgressOut)
def progress(current_user: CurrentUser, db: DbSession) -> ProgressOut:
    return get_progress(db, current_user)
