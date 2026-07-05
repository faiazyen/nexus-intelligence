"""Unit tests for the Brain retriever and Memory Manager adjustments (no DB/LLM)."""

from __future__ import annotations

import uuid

from app.agents.business_brain import rank_documents
from app.agents.memory_manager import (
    ADJUSTMENT_BOUND,
    apply_adjustment,
)
from app.db.models import BusinessContextDoc


def make_doc(title: str, content: str) -> BusinessContextDoc:
    return BusinessContextDoc(
        id=uuid.uuid4(), org_id=uuid.uuid4(), doc_type="general",
        title=title, content=content,
    )


class TestRetriever:
    def test_relevant_doc_ranks_first(self):
        pricing = make_doc("Pricing", "Discovery sprint costs 15K, roadmap 45K, retainer 8K monthly pricing")
        casestudy = make_doc("Case study", "We won a healthtech transformation engagement")
        ranked = rank_documents([casestudy, pricing], "what is our pricing for a discovery sprint?", k=2)
        assert ranked[0] is pricing

    def test_no_overlap_returns_empty(self):
        doc = make_doc("Ops", "logistics warehouse optimization")
        assert rank_documents([doc], "quantum blockchain gardening") == []

    def test_k_limits_results(self):
        docs = [make_doc(f"doc{i}", "pricing pricing pricing") for i in range(10)]
        assert len(rank_documents(docs, "pricing", k=3)) == 3

    def test_empty_question_returns_head(self):
        docs = [make_doc("a", "x"), make_doc("b", "y")]
        assert rank_documents(docs, "", k=1) == docs[:1]


class TestMemoryAdjustments:
    def test_positive_outcome_increments(self):
        assert apply_adjustment(0, "replied") == 1
        assert apply_adjustment(0, "meeting_booked") == 1

    def test_negative_outcome_decrements(self):
        assert apply_adjustment(0, "no_response") == -1
        assert apply_adjustment(0, "bounced") == -1

    def test_bounded_above(self):
        assert apply_adjustment(ADJUSTMENT_BOUND, "replied") == ADJUSTMENT_BOUND

    def test_bounded_below(self):
        assert apply_adjustment(-ADJUSTMENT_BOUND, "bounced") == -ADJUSTMENT_BOUND

    def test_unknown_outcome_no_change(self):
        assert apply_adjustment(3, "ghosted") == 3
