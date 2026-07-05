"""Unit tests for the pure Action Queue helpers (no database)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.db.models import Signal
from app.services.queue import (
    DEFAULT_WINDOW_ESTIMATE_DAYS,
    build_signal_summary,
    compute_window_estimate,
    select_strongest_signal,
)

NOW = datetime(2026, 7, 5, 12, 0, 0, tzinfo=timezone.utc)


def make_signal(signal_type: str, days_ago: float = 0.0, title: str = "") -> Signal:
    return Signal(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        signal_type=signal_type,
        detected_at=NOW - timedelta(days=days_ago),
        title=title or f"{signal_type} event",
        status="classified",
    )


class TestStrongestSignal:
    def test_empty_returns_none(self):
        assert select_strongest_signal([], NOW) is None

    def test_heavier_type_wins_at_same_age(self):
        news = make_signal("news")
        notice = make_signal("procurement_notice")
        assert select_strongest_signal([news, notice], NOW) is notice

    def test_fresh_beats_stale_same_type(self):
        fresh = make_signal("funding", days_ago=1)
        stale = make_signal("funding", days_ago=100)
        assert select_strongest_signal([stale, fresh], NOW) is fresh


class TestWindowEstimate:
    def test_none_signal_uses_default(self):
        assert compute_window_estimate(None, NOW) == DEFAULT_WINDOW_ESTIMATE_DAYS

    def test_fresh_signal_returns_full_window(self):
        signal = make_signal("leadership_change", days_ago=0)
        assert compute_window_estimate(signal, NOW) == 90

    def test_aged_signal_subtracts_age(self):
        signal = make_signal("funding", days_ago=20)  # 60-day window
        assert compute_window_estimate(signal, NOW) == 40

    def test_expired_window_floors_at_one_day(self):
        signal = make_signal("news", days_ago=400)
        assert compute_window_estimate(signal, NOW) == 1


class TestSignalSummary:
    def test_empty_signals(self):
        assert build_signal_summary([], NOW) == "No active signals."

    def test_lists_strongest_first_max_three(self):
        signals = [
            make_signal("news", title="minor news"),
            make_signal("procurement_notice", title="RFI published"),
            make_signal("funding", title="Series B"),
            make_signal("filing", title="8-K filed"),
        ]
        summary = build_signal_summary(signals, NOW)
        assert summary.startswith("procurement_notice: RFI published")
        assert summary.count("|") == 2  # exactly 3 segments

    def test_long_titles_truncated(self):
        signal = make_signal("news", title="x" * 300)
        summary = build_signal_summary([signal], NOW)
        assert "..." in summary
        assert len(summary) < 200
