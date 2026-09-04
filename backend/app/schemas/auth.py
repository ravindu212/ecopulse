from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def normalize_email(value: str) -> str:
    return value.strip().lower()


class RegistrationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        normalized_name = value.strip()
        if len(normalized_name) < 2:
            raise ValueError("Name must contain at least 2 characters")
        return normalized_name

    @field_validator("email", mode="after")
    @classmethod
    def normalize_registration_email(cls, value: EmailStr) -> str:
        return normalize_email(str(value))


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="after")
    @classmethod
    def normalize_login_email(cls, value: EmailStr) -> str:
        return normalize_email(str(value))


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    xp: int
    current_streak: int
    longest_streak: int
    last_action_date: date | None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
