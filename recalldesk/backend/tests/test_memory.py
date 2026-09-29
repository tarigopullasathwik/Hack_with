"""
Tests for Hindsight memory operations (retain, recall, reflect).
Uses the in-process fallback store so no Hindsight server is required.
"""
import pytest
from app import hindsight as mem


def test_hindsight_retain_fallback():
    """retain() should succeed in fallback mode."""
    result = mem.retain(
        customer_id="mem-test-001",
        content="Customer had payment failure. Cache clearing failed. Billing profile update worked.",
        context="test",
        metadata={"test": True},
    )
    assert result["success"] is True


def test_hindsight_recall_fallback():
    """recall() should return relevant memories from fallback store."""
    # First retain something
    mem.retain(
        customer_id="mem-test-002",
        content="Cache clearing did NOT fix the payment issue for this customer.",
        context="test_recall",
    )
    # Now recall
    result = mem.recall(
        customer_id="mem-test-002",
        query="payment issue cache clearing",
    )
    assert result["success"] is True
    assert result["count"] > 0
    assert any("payment" in m["text"].lower() for m in result["memories"])


def test_hindsight_recall_no_memories():
    """recall() for a customer with no memories returns empty list."""
    result = mem.recall(
        customer_id="cust-nobody",
        query="billing issue",
    )
    assert result["success"] is True
    assert result["memories"] == []


def test_hindsight_failed_step_is_stored():
    """Verify that a failed troubleshooting step is stored and retrievable."""
    mem.retain(
        customer_id="mem-test-003",
        content="FAILED STEPS (do not retry): Clear browser cache. This step did NOT work for customer.",
        context="outcome_tracking",
    )
    result = mem.recall(
        customer_id="mem-test-003",
        query="cache clearing failed",
    )
    assert result["success"] is True
    assert result["count"] > 0
    assert any("cache" in m["text"].lower() for m in result["memories"])


def test_hindsight_successful_resolution_stored():
    """Verify that a successful resolution is stored and retrievable."""
    mem.retain(
        customer_id="mem-test-004",
        content="SUCCESSFUL RESOLUTION STEP: Updating billing profile resolved the payment issue.",
        context="resolution",
    )
    result = mem.recall(
        customer_id="mem-test-004",
        query="billing profile resolved",
    )
    assert result["success"] is True
    assert any("billing profile" in m["text"].lower() for m in result["memories"])


def test_hindsight_reflect_fallback():
    """reflect() returns an answer from fallback store."""
    mem.retain(
        customer_id="mem-test-005",
        content="Customer prefers Slack over email for support communications.",
        context="preference",
    )
    result = mem.reflect(
        customer_id="mem-test-005",
        query="customer communication preference",
    )
    assert result["success"] is True
    assert len(result["answer"]) > 0


def test_hindsight_list_memories():
    """list_memories() returns memories for a customer."""
    mem.retain(
        customer_id="mem-test-006",
        content="Test memory entry for listing.",
        context="list_test",
    )
    result = mem.list_memories("mem-test-006")
    assert result["success"] is True
    assert result["count"] > 0


def test_demo_customer_memories_seeded():
    """Verify that demo customer memories were pre-seeded."""
    result = mem.recall(
        customer_id="cust-001",
        query="billing payment failure cache clearing",
    )
    assert result["success"] is True
    assert result["count"] > 0
    # The seeded memory about cache clearing failing should be there
    texts = " ".join(m["text"] for m in result["memories"]).lower()
    assert "cache" in texts or "billing" in texts or "payment" in texts


def test_create_bank_fallback():
    """create_bank() creates a bank entry in fallback mode."""
    result = mem.create_bank("mem-bank-test", "Test Customer", "business")
    assert result["success"] is True
    assert "bank_id" in result


def test_memory_mode_without_memory():
    """Without-memory mode returns no recalled memories (tested via API)."""
    # This is tested at agent level; here just confirm fallback store isolation
    bank_id = "recalldesk-customer-cust-001"
    from app.hindsight.manager import _fallback_store
    assert bank_id in _fallback_store
    assert len(_fallback_store[bank_id]) > 0
