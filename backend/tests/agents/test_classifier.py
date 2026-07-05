"""Unit tests for the Intent Classifier's parsing and sanitization (no LLM)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.agents.intent_classifier import (
    extract_json,
    heuristic_classification,
    sanitize_classification,
)
from app.db.models import Signal


def make_signal(signal_type: str = "funding", title: str = "Raised $10M") -> Signal:
    return Signal(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        signal_type=signal_type,
        title=title,
        detected_at=datetime(2026, 7, 5, tzinfo=timezone.utc),
        status="new",
    )


class TestExtractJson:
    def test_clean_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_json_wrapped_in_prose(self):
        text = 'Here is the classification:\n{"urgency_tier": "HOT"}\nDone.'
        assert extract_json(text) == {"urgency_tier": "HOT"}

    def test_garbage_returns_none(self):
        assert extract_json("not json at all") is None

    def test_empty_and_none_safe(self):
        assert extract_json("") is None

    def test_non_object_json_returns_none(self):
        assert extract_json("[1, 2, 3]") is None


class TestHeuristics:
    def test_procurement_notice_is_hot_confirmed(self):
        result = heuristic_classification(make_signal("procurement_notice"))
        assert result["urgency_tier"] == "HOT"
        assert result["budget_implication"] == "CONFIRMED"

    def test_unknown_type_gets_default(self):
        result = heuristic_classification(make_signal("something_odd"))
        assert result["urgency_tier"] == "COOL"
        assert result["budget_implication"] == "NONE"

    def test_summary_falls_back_to_title(self):
        result = heuristic_classification(make_signal(title="Big announcement"))
        assert result["summary"] == "Big announcement"


class TestSanitize:
    def test_valid_payload_passes_through(self):
        signal = make_signal()
        payload = {
            "urgency_tier": "hot",
            "budget_implication": "probable",
            "decision_maker_involved": True,
            "days_to_action_window": 45,
            "summary": "Budget just unlocked.",
        }
        result = sanitize_classification(payload, signal)
        assert result["urgency_tier"] == "HOT"
        assert result["budget_implication"] == "PROBABLE"
        assert result["days_to_action_window"] == 45
        assert result["summary"] == "Budget just unlocked."

    def test_invalid_tier_falls_back_to_heuristic(self):
        signal = make_signal("funding")
        result = sanitize_classification({"urgency_tier": "BLAZING"}, signal)
        assert result["urgency_tier"] == heuristic_classification(signal)["urgency_tier"]

    def test_out_of_range_window_falls_back(self):
        signal = make_signal("funding")
        result = sanitize_classification({"days_to_action_window": 9999}, signal)
        assert result["days_to_action_window"] == 60

    def test_non_numeric_window_falls_back(self):
        signal = make_signal("job_post")
        result = sanitize_classification({"days_to_action_window": "soon"}, signal)
        assert result["days_to_action_window"] == 45
