"""Initial schema: all 11 NEXUS tables.

Revision ID: 001_initial
Revises: None
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("plan", sa.String(32), nullable=False, server_default="solo"),
        sa.Column("api_credits_remaining", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("settings", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("plan_tier", sa.String(32), nullable=False, server_default="solo"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "icp_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("target_industries", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("company_size_min", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("company_size_max", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("titles_targeted", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("geographies", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("tech_stack_keywords", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("offer_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "business_context_docs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("doc_type", sa.String(64), nullable=False, server_default="general"),
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding_id", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False, server_default=""),
        sa.Column("industry", sa.String(128), nullable=False, server_default=""),
        sa.Column("employee_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue_estimate", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("geography", sa.String(128), nullable=False, server_default=""),
        sa.Column("tech_stack", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("last_enriched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_accounts_org_id", "accounts", ["org_id"])

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("signal_type", sa.String(64), nullable=False),
        sa.Column("source", sa.String(128), nullable=False, server_default=""),
        sa.Column("title", sa.String(512), nullable=False, server_default=""),
        sa.Column("raw_data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("urgency_tier", sa.String(8), nullable=True),
        sa.Column("budget_implication", sa.String(16), nullable=True),
        sa.Column("decision_maker_involved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("days_to_action_window", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="new"),
    )
    op.create_index("ix_signals_account_id", "signals", ["account_id"])
    op.create_index("ix_signals_status", "signals", ["status"])
    op.create_index("ix_signals_detected_at", "signals", ["detected_at"])

    op.create_table(
        "account_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("urgency", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fit", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("budget_probability", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("composite_nexus_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("signal_ids", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_account_scores_account_id", "account_scores", ["account_id"])

    op.create_table(
        "action_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("nexus_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("signal_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("days_in_window_estimate", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("entered_queue_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
    )
    op.create_index("ix_action_queue_status", "action_queue", ["status"])

    op.create_table(
        "outreach_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("variant", sa.String(16), nullable=False, server_default="analytical"),
        sa.Column("email_subject", sa.String(255), nullable=False, server_default=""),
        sa.Column("email_body", sa.Text(), nullable=False, server_default=""),
        sa.Column("linkedin_message", sa.Text(), nullable=False, server_default=""),
        sa.Column("call_script", sa.Text(), nullable=False, server_default=""),
        sa.Column("positioning_frame", sa.Text(), nullable=False, server_default=""),
        sa.Column("signal_reference", sa.Text(), nullable=False, server_default=""),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reply_received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_outreach_drafts_account_id", "outreach_drafts", ["account_id"])

    op.create_table(
        "brain_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "brain_briefings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("briefing_date", sa.Date(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_brain_briefings_org_date", "brain_briefings", ["org_id", "briefing_date"])


def downgrade() -> None:
    for table in (
        "brain_briefings",
        "brain_conversations",
        "outreach_drafts",
        "action_queue",
        "account_scores",
        "signals",
        "accounts",
        "business_context_docs",
        "icp_profiles",
        "users",
        "organizations",
    ):
        op.drop_table(table)
