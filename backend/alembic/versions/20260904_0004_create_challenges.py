"""create challenge foundation tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260904_0004"
down_revision = "20260904_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("challenges", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("title", sa.String(160), nullable=False), sa.Column("slug", sa.String(180), nullable=False, unique=True), sa.Column("description", sa.Text(), nullable=False), sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.create_table("challenge_actions", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("challenges.id"), nullable=False), sa.Column("action_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("climate_actions.id"), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"), sa.UniqueConstraint("challenge_id", "action_id", name="uq_challenge_actions_challenge_action"))
    op.create_table("user_challenges", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("challenge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("challenges.id"), nullable=False), sa.Column("status", sa.String(12), nullable=False, server_default="active"), sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("user_id", "challenge_id", name="uq_user_challenges_user_challenge"))
    op.create_index("ix_user_challenges_user_id", "user_challenges", ["user_id"])
    op.create_index("ix_user_challenges_user_status", "user_challenges", ["user_id", "status"])


def downgrade() -> None:
    op.drop_table("user_challenges")
    op.drop_table("challenge_actions")
    op.drop_table("challenges")
