from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ClimateAction(Base):
    __tablename__ = "climate_actions"
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    impact_level: Mapped[str] = mapped_column(String(10), nullable=False)
    estimated_co2e_kg: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    user_actions: Mapped[list["UserAction"]] = relationship(back_populates="action")
    challenge_actions: Mapped[list["ChallengeAction"]] = relationship(back_populates="action")


class UserAction(Base):
    __tablename__ = "user_actions"
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action_id: Mapped[UUID] = mapped_column(ForeignKey("climate_actions.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="started")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_co2e_kg_awarded: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    user: Mapped["User"] = relationship(back_populates="user_actions")
    action: Mapped[ClimateAction] = relationship(back_populates="user_actions")
