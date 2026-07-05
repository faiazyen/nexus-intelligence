"""Unit tests for the NEXUS scoring engine (pure, no database)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.db.models import Account, ICPProfile, Signal
from app.services.scoring import (
    QUEUE_THRESHOLD,
    SIGNAL_BUDGET_WEIGHTS,
    TIMING_WINDOWS_DAYS,
    compute_budget_probability,
    compute_fit,
    compute_nexus_score,
    compute_urgency,
    recency_decay,
    score_account,
)

NOW = datetime(2026, 7, 5, 12, 0, 0, tzinfo=timezone.utc)


def make_signal(signal_type: str, days_ago: float = 0.0) -> Signal:
    return Signal(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        signal_type=signal_type,
        detected_at=NOW - timedelta(days=days_ago),
        title=f"test {signal_type}",
        status="classified",
    )


def make_account(**overrides) -> Account:
    defaults = dict(
        id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        company_name="Testco",
        industry="saas",
        employee_count=100,
        geography="United States",
        tech_stack={"crm": "Salesforce"},
    )
    defaults.update(overrides)
    return Account(**defaults)


def make_icp(**overrides) -> ICPProfile:
    defaults = dict(
        id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        target_industries=["saas"],
        company_size_min=50,
        company_size_max=500,
        titles_targeted=["CEO"],
        geographies=["United States"],
        tech_stack_keywords=["Salesforce"],
        offer_description="consulting",
    )
    defaults.update(overrides)
    return ICPProfile(**defaults)


# --- Budget probability -------------------------------------------------------


class TestBudgetProbability:
    def test_each_canonical_type_contributes_its_contract_weight(self):
        for signal_type, weight in SIGNAL_BUDGET_WEIGHTS.items():
            assert compute_budget_probability([make_signal(signal_type)]) == weight

    def test_additive_across_signals(self):
        signals = [make_signal("job_post"), make_signal("funding")]
        assert compute_budget_probability(signals) == 15 + 25

    def test_caps_at_100(self):
        signals = [make_signal("procurement_notice") for _ in range(4)]  # 160 raw
        assert compute_budget_probability(signals) == 100

    def test_unknown_type_gets_default_weight(self):
        assert compute_budget_probability([make_signal("mystery")]) == 5

    def test_empty_is_zero(self):
        assert compute_budget_probability([]) == 0


# --- Urgency -------------------------------------------------------------------


class TestUrgency:
    def test_no_signals_is_zero(self):
        assert compute_urgency([], NOW) == 0

    def test_fresh_heavy_signal_maxes_base(self):
        # procurement_notice has the max type weight -> strength 1.0.
        assert compute_urgency([make_signal("procurement_notice")], NOW) == 100

    def test_fresh_light_signal_scores_low(self):
        urgency = compute_urgency([make_signal("news")], NOW)
        assert 0 < urgency < 30

    def test_recency_decay_full_inside_window(self):
        signal = make_signal("job_post", days_ago=TIMING_WINDOWS_DAYS["job_post"] - 1)
        assert recency_decay(signal, NOW) == 1.0

    def test_recency_decay_zero_after_double_window(self):
        window = TIMING_WINDOWS_DAYS["news"]
        signal = make_signal("news", days_ago=2 * window + 1)
        assert recency_decay(signal, NOW) == 0.0

    def test_recency_decay_partial_in_decay_band(self):
        window = TIMING_WINDOWS_DAYS["funding"]
        signal = make_signal("funding", days_ago=window * 1.5)
        assert 0.0 < recency_decay(signal, NOW) < 1.0

    def test_concurrent_signals_raise_urgency(self):
        one = compute_urgency([make_signal("job_post")], NOW)
        three = compute_urgency(
            [make_signal("job_post"), make_signal("news"), make_signal("filing")], NOW
        )
        assert three > one

    def test_clamped_to_100(self):
        signals = [make_signal("procurement_notice") for _ in range(10)]
        assert compute_urgency(signals, NOW) == 100


# --- Fit -----------------------------------------------------------------------


class TestFit:
    def test_perfect_match_is_100(self):
        assert compute_fit(make_account(), make_icp()) == 100

    def test_no_icp_is_neutral_50(self):
        assert compute_fit(make_account(), None) == 50

    def test_industry_mismatch_drops_35(self):
        account = make_account(industry="mining")
        assert compute_fit(account, make_icp()) == 65

    def test_size_outside_range_but_within_2x_gets_partial(self):
        account = make_account(employee_count=800)  # max 500, within 2x
        fit = compute_fit(account, make_icp())
        assert fit == 100 - 25 + 10

    def test_size_far_outside_gets_zero_size_points(self):
        account = make_account(employee_count=50_000)
        assert compute_fit(account, make_icp()) == 75

    def test_geography_mismatch_drops_20(self):
        account = make_account(geography="Japan")
        assert compute_fit(account, make_icp()) == 80

    def test_tech_stack_partial_credit(self):
        icp = make_icp(tech_stack_keywords=["Salesforce", "SAP"])
        fit = compute_fit(make_account(), icp)  # matches 1 of 2 -> 10 of 20
        assert fit == 90

    def test_unconstrained_dimensions_award_full_points(self):
        icp = make_icp(target_industries=[], geographies=[], tech_stack_keywords=[])
        assert compute_fit(make_account(industry="anything", geography="Mars"), icp) == 100


# --- Composite ------------------------------------------------------------------


class TestComposite:
    def test_contract_formula(self):
        assert compute_nexus_score(100, 100, 100) == 100
        assert compute_nexus_score(80, 90, 70) == round(80 * 90 * 70 / 10000)

    def test_zero_any_dimension_zeroes_composite(self):
        assert compute_nexus_score(0, 100, 100) == 0
        assert compute_nexus_score(100, 0, 100) == 0

    def test_out_of_range_inputs_are_clamped(self):
        assert compute_nexus_score(150, 150, 150) == 100
        assert compute_nexus_score(-5, 50, 50) == 0

    def test_threshold_routing_example(self):
        """A hot multi-signal ICP-fit account must clear the queue threshold."""
        account = make_account(industry="healthtech")
        icp = make_icp(target_industries=["healthtech"])
        signals = [
            make_signal("earnings_language", days_ago=8),
            make_signal("leadership_change", days_ago=12),
            make_signal("funding", days_ago=3),
        ]
        score = score_account(account, icp, signals, NOW)
        assert score.composite_nexus_score >= QUEUE_THRESHOLD

    def test_cold_account_stays_below_threshold(self):
        account = make_account(industry="mining", geography="Mars", employee_count=9)
        signals = [make_signal("news", days_ago=29)]
        score = score_account(account, make_icp(), signals, NOW)
        assert score.composite_nexus_score < QUEUE_THRESHOLD


# --- score_account convenience ----------------------------------------------------


class TestScoreAccount:
    def test_returns_persistable_row_with_explanation(self):
        account = make_account()
        signals = [make_signal("funding")]
        score = score_account(account, make_icp(), signals, NOW)
        assert score.account_id == account.id
        assert score.signal_ids == [str(signals[0].id)]
        assert "urgency" in score.explanation
        assert str(score.composite_nexus_score) in score.explanation

    def test_no_signals_notes_it_in_explanation(self):
        score = score_account(make_account(), make_icp(), [], NOW)
        assert score.composite_nexus_score == 0
        assert "no signals" in score.explanation.lower()
