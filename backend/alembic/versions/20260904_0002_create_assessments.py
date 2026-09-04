"""create assessments table"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260904_0002"
down_revision = "20260904_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("assessments", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False), sa.Column("transport_score", sa.Integer(), nullable=False), sa.Column("energy_score", sa.Integer(), nullable=False), sa.Column("food_score", sa.Integer(), nullable=False), sa.Column("waste_score", sa.Integer(), nullable=False), sa.Column("overall_score", sa.Integer(), nullable=False), sa.Column("lowest_category", sa.String(length=20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_assessments_user_id", "assessments", ["user_id"])
    op.create_index("ix_assessments_user_created_at", "assessments", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_assessments_user_created_at", table_name="assessments")
    op.drop_index("ix_assessments_user_id", table_name="assessments")
    op.drop_table("assessments")
