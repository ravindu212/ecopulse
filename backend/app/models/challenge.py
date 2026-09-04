from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    challenge_actions: Mapped[list["ChallengeAction"]] = relationship(back_populates="challenge")
    memberships: Mapped[list["UserChallenge"]] = relationship(back_populates="challenge")


class ChallengeAction(Base):
    __tablename__ = "challenge_actions"
    __table_args__ = (UniqueConstraint("challenge_id", "action_id", name="uq_challenge_actions_challenge_action"),)

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    challenge_id: Mapped[UUID] = mapped_column(ForeignKey("challenges.id"), nullable=False)
    action_id: Mapped[UUID] = mapped_column(ForeignKey("climate_actions.id"), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    challenge: Mapped[Challenge] = relationship(back_populates="challenge_actions")
    action: Mapped["ClimateAction"] = relationship(back_populates="challenge_actions")


class UserChallenge(Base):
    __tablename__ = "user_challenges"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_user_challenges_user_challenge"),)

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    challenge_id: Mapped[UUID] = mapped_column(ForeignKey("challenges.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    challenge: Mapped[Challenge] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="challenges")
