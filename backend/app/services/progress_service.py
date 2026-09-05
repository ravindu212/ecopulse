from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.action import ClimateAction, UserAction
from app.models.assessment import Assessment
from app.models.user import User
from app.schemas.progress import AssessmentHistoryItem, CategoryActivity, ProgressOut, ProgressRecentActivity, ProgressSummary


_CATEGORIES = ("transport", "energy", "food", "waste")


def get_progress(db: Session, user: User) -> ProgressOut:
    completed = UserAction.status == "completed"
    completed_actions, avoided = db.execute(
        select(
            func.count(UserAction.id),
            func.coalesce(func.sum(UserAction.estimated_co2e_kg_awarded), 0),
        ).where(UserAction.user_id == user.id, completed)
    ).one()

    category_rows = db.execute(
        select(
            ClimateAction.category,
            func.count(UserAction.id),
            func.coalesce(func.sum(UserAction.estimated_co2e_kg_awarded), 0),
        )
        .join(UserAction, UserAction.action_id == ClimateAction.id)
        .where(UserAction.user_id == user.id, completed)
        .group_by(ClimateAction.category)
    ).all()
    category_totals = {category: (int(count), float(total or 0)) for category, count, total in category_rows}
    category_activity = [
        CategoryActivity(
            category=category,
            completed_actions=category_totals.get(category, (0, 0.0))[0],
            estimated_co2e_kg_avoided=category_totals.get(category, (0, 0.0))[1],
        )
        for category in _CATEGORIES
    ]

    assessments = list(
        db.scalars(
            select(Assessment)
            .where(Assessment.user_id == user.id)
            .order_by(Assessment.created_at.asc())
        )
    )
    assessment_history = [
        AssessmentHistoryItem(
            assessment_date=assessment.created_at,
            overall_score=assessment.overall_score,
            transport_score=assessment.transport_score,
            energy_score=assessment.energy_score,
            food_score=assessment.food_score,
            waste_score=assessment.waste_score,
        )
        for assessment in assessments
    ]

    recent_rows = db.execute(
        select(
            ClimateAction.title,
            ClimateAction.category,
            UserAction.completed_at,
            UserAction.xp_awarded,
            UserAction.estimated_co2e_kg_awarded,
        )
        .join(ClimateAction, ClimateAction.id == UserAction.action_id)
        .where(UserAction.user_id == user.id, completed)
        .order_by(UserAction.completed_at.desc())
        .limit(5)
    ).all()
    recent_activity = [
        ProgressRecentActivity(
            title=title,
            category=category,
            completed_at=completed_at,
            xp_awarded=xp_awarded,
            estimated_co2e_kg_awarded=float(impact or 0),
        )
        for title, category, completed_at, xp_awarded, impact in recent_rows
        if completed_at is not None
    ]

    return ProgressOut(
        summary=ProgressSummary(
            xp=user.xp,
            current_streak=user.current_streak,
            longest_streak=user.longest_streak,
            completed_actions=int(completed_actions),
            estimated_co2e_kg_avoided=float(avoided or 0),
        ),
        category_activity=category_activity,
        assessment_history=assessment_history,
        recent_activity=recent_activity,
    )
