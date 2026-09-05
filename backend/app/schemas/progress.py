from datetime import datetime

from pydantic import BaseModel


class ProgressSummary(BaseModel):
    xp: int
    current_streak: int
    longest_streak: int
    completed_actions: int
    estimated_co2e_kg_avoided: float


class CategoryActivity(BaseModel):
    category: str
    completed_actions: int
    estimated_co2e_kg_avoided: float


class AssessmentHistoryItem(BaseModel):
    assessment_date: datetime
    overall_score: int
    transport_score: int
    energy_score: int
    food_score: int
    waste_score: int


class ProgressRecentActivity(BaseModel):
    title: str
    category: str
    completed_at: datetime
    xp_awarded: int
    estimated_co2e_kg_awarded: float


class ProgressOut(BaseModel):
    summary: ProgressSummary
    category_activity: list[CategoryActivity]
    assessment_history: list[AssessmentHistoryItem]
    recent_activity: list[ProgressRecentActivity]
