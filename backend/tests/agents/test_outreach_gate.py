"""Unit tests for the Outreach Writer quality gate and fallback templates."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.agents.outreach_writer import (
    VARIANTS,
    count_sentences,
    quality_violations,
    template_draft,
)
from app.db.models import Account, Signal

SIGNAL_TITLE = "Northwind raises $24M Series B led by Insight Partners"


def make_account() -> Account:
    return Account(
        id=uuid.uuid4(), org_id=uuid.uuid4(), company_name="Northwind SaaS",
        industry="saas", employee_count=95, geography="United States",
    )


def make_signal() -> Signal:
    return Signal(
        id=uuid.uuid4(), account_id=uuid.uuid4(), signal_type="funding",
        title=SIGNAL_TITLE, urgency_tier="HOT",
        detected_at=datetime(2026, 7, 5, tzinfo=timezone.utc), status="classified",
    )


def good_draft() -> dict:
    return {
        "email_subject": "Series B and the next 90 days",
        "email_body": (
            "Saw Northwind raised a $24M Series B led by Insight Partners. "
            "The next 90 days decide whether that capital compounds or leaks into unowned priorities. "
            "Open to a 15 minute call this week?"
        ),
        "linkedin_message": "Congrats on the Series B raises announcement. Worth 15 minutes to compare notes?",
        "call_script": "Hi, calling about the Series B at Northwind, not a pitch. Raises this size open a short window. Is that on your radar?",
        "positioning_frame": "Funding signal means new GTM mandate.",
    }


class TestSentenceCount:
    def test_counts_terminal_punctuation(self):
        assert count_sentences("One. Two! Three?") == 3

    def test_empty_is_zero(self):
        assert count_sentences("") == 0


class TestQualityGate:
    def test_good_draft_passes(self):
        assert quality_violations(good_draft(), SIGNAL_TITLE) == []

    def test_banned_phrases_rejected(self):
        draft = good_draft()
        draft["email_body"] = "Hope this finds you well. " + draft["email_body"]
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("banned phrase" in v for v in violations)

    def test_four_sentence_body_rejected(self):
        draft = good_draft()
        draft["email_body"] += " One more sentence here."
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("sentences" in v for v in violations)

    def test_em_dash_rejected(self):
        draft = good_draft()
        draft["linkedin_message"] = "Congrats — worth Northwind raises a chat?"
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("em dash" in v for v in violations)

    def test_double_hyphen_rejected(self):
        draft = good_draft()
        draft["call_script"] = draft["call_script"] + " -- quick one"
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("em dash" in v for v in violations)

    def test_long_subject_rejected(self):
        draft = good_draft()
        draft["email_subject"] = "this subject line has way too many words in it"
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("subject" in v for v in violations)

    def test_missing_signal_reference_rejected(self):
        draft = good_draft()
        draft["email_body"] = "We do great work. You need help. Call me?"
        draft["email_subject"] = "Quick chat"
        draft["linkedin_message"] = "Quick chat?"
        draft["call_script"] = "Just checking in."
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("signal" in v for v in violations)

    def test_empty_body_rejected(self):
        draft = good_draft()
        draft["email_body"] = ""
        violations = quality_violations(draft, SIGNAL_TITLE)
        assert any("empty" in v for v in violations)


class TestTemplateFallback:
    def test_every_variant_passes_the_gate(self):
        account, signal = make_account(), make_signal()
        for variant in VARIANTS:
            draft = template_draft(variant, account, signal, "ops consulting")
            assert quality_violations(draft, signal.title) == [], variant

    def test_template_references_company(self):
        draft = template_draft("analytical", make_account(), make_signal(), "")
        assert "Northwind" in draft["email_subject"] + draft["email_body"]
