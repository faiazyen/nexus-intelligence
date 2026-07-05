"""pipeline_events audit table.

Revision ID: 002_pipeline_events
Revises: 001_initial
Create Date: 2026-07-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_pipeline_events"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pipeline_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("detail", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_pipeline_events_org_id", "pipeline_events", ["org_id"])
    op.create_index("ix_pipeline_events_created_at", "pipeline_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("pipeline_events")
