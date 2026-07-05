"""NEXUS Intelligence — SQLAlchemy 2.0 models.

Canonical schema for the whole platform. Every workstream imports from here;
nothing outside this file defines tables. Mirrors docs/CONTRACT.md.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(32), default="solo")  # solo|agency|enterprise
    api_credits_remaining: Mapped[int] = mapped_column(Integer, default=50)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    icp_profiles: Mapped[list["ICPProfile"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    plan_tier: Mapped[str] = mapped_column(String(32), default="solo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    organization: Mapped[Organization] = relationship(back_populates="users")


class ICPProfile(Base):
    __tablename__ = "icp_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    target_industries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    company_size_min: Mapped[int] = mapped_column(Integer, default=10)
    company_size_max: Mapped[int] = mapped_column(Integer, default=1000)
    titles_targeted: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    geographies: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    tech_stack_keywords: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    offer_description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    organization: Mapped[Organization] = relationship(back_populates="icp_profiles")


class BusinessContextDoc(Base):
    __tablename__ = "business_context_docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(64), default="general")  # proposal|case_study|pricing|win_loss|general
    title: Mapped[str] = mapped_column(String(255), default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # Qdrant point id
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), default="")
    industry: Mapped[str] = mapped_column(String(128), default="")
    employee_count: Mapped[int] = mapped_column(Integer, default=0)
    revenue_estimate: Mapped[int] = mapped_column(Integer, default=0)  # USD
    geography: Mapped[str] = mapped_column(String(128), default="")
    tech_stack: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    signals: Mapped[list["Signal"]] = relationship(back_populates="account")
    scores: Mapped[list["AccountScore"]] = relationship(back_populates="account")


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(64), nullable=False)  # canonical strings, CONTRACT.md
    source: Mapped[str] = mapped_column(String(128), default="")  # linkedin_jobs|sec_edgar|sam_gov|newsapi|crunchbase|manual
    title: Mapped[str] = mapped_column(String(512), default="")
    raw_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    urgency_tier: Mapped[str | None] = mapped_column(String(8), nullable=True)  # HOT|WARM|COOL
    budget_implication: Mapped[str | None] = mapped_column(String(16), nullable=True)  # CONFIRMED|PROBABLE|POSSIBLE|NONE
    decision_maker_involved: Mapped[bool] = mapped_column(Boolean, default=False)
    days_to_action_window: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="new")  # new|classified|scored|archived

    account: Mapped[Account] = relationship(back_populates="signals")


class AccountScore(Base):
    __tablename__ = "account_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    urgency: Mapped[int] = mapped_column(Integer, default=0)
    fit: Mapped[int] = mapped_column(Integer, default=0)
    budget_probability: Mapped[int] = mapped_column(Integer, default=0)
    composite_nexus_score: Mapped[int] = mapped_column(Integer, default=0)
    signal_ids: Mapped[list] = mapped_column(JSONB, default=list)
    explanation: Mapped[str] = mapped_column(Text, default="")
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    account: Mapped[Account] = relationship(back_populates="scores")


class ActionQueueEntry(Base):
    __tablename__ = "action_queue"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    nexus_score: Mapped[int] = mapped_column(Integer, default=0)
    signal_summary: Mapped[str] = mapped_column(Text, default="")
    days_in_window_estimate: Mapped[int] = mapped_column(Integer, default=30)
    entered_queue_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending|outreach_generated|contacted|dismissed|converted

    account: Mapped[Account] = relationship()


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    variant: Mapped[str] = mapped_column(String(16), default="analytical")  # assertive|analytical|challenger
    email_subject: Mapped[str] = mapped_column(String(255), default="")
    email_body: Mapped[str] = mapped_column(Text, default="")
    linkedin_message: Mapped[str] = mapped_column(Text, default="")
    call_script: Mapped[str] = mapped_column(Text, default="")
    positioning_frame: Mapped[str] = mapped_column(Text, default="")
    signal_reference: Mapped[str] = mapped_column(Text, default="")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reply_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)  # replied|meeting_booked|no_response|bounced
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    account: Mapped[Account] = relationship()


class BrainConversation(Base):
    __tablename__ = "brain_conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user|assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BrainBriefing(Base):
    __tablename__ = "brain_briefings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    briefing_date: Mapped[date] = mapped_column(Date, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
