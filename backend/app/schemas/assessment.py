from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssessmentSubmission(BaseModel):
    answers: dict[str, str] = Field(min_length=1)


class AssessmentOption(BaseModel):
    id: str
    label: str


class AssessmentQuestion(BaseModel):
    id: str
    category: str
    text: str
    options: list[AssessmentOption]


class AssessmentResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transport_score: int
    energy_score: int
    food_score: int
    waste_score: int
    overall_score: int
    lowest_category: str
    created_at: datetime
