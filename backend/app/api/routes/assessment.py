from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentQuestion, AssessmentResult, AssessmentSubmission
from app.services.assessment_service import calculate_scores, public_questions


router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.get("/questions", response_model=list[AssessmentQuestion])
def questions() -> list[dict[str, object]]:
    return public_questions()


@router.post("", response_model=AssessmentResult, status_code=status.HTTP_201_CREATED)
def create_assessment(submission: AssessmentSubmission, current_user: CurrentUser, db: DbSession) -> Assessment:
    try:
        scores = calculate_scores(submission.answers)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from None
    assessment = Assessment(
        user_id=current_user.id,
        answers=submission.answers,
        transport_score=scores["transport"],
        energy_score=scores["energy"],
        food_score=scores["food"],
        waste_score=scores["waste"],
        overall_score=scores["overall_score"],
        lowest_category=scores["lowest_category"],
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/latest", response_model=AssessmentResult)
def latest_assessment(current_user: CurrentUser, db: DbSession) -> Assessment:
    assessment = db.scalar(select(Assessment).where(Assessment.user_id == current_user.id).order_by(Assessment.created_at.desc(), Assessment.id.desc()).limit(1))
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No assessment found")
    return assessment
