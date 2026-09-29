"""Tests for ticket creation, update, and escalation."""
import pytest
import json
from app.models import Customer, CustomerPlan, CustomerStatus


def test_create_ticket(client, db):
    # Create a temp customer
    from app.models import Customer
    c = Customer(
        id="tk-test-001", name="Tk User", email="tk.user.unique@test.com",
        company="Test", plan=CustomerPlan.BUSINESS, status=CustomerStatus.ACTIVE,
    )
    db.add(c)
    db.commit()

    resp = client.post("/api/v1/tickets", json={
        "customer_id": "tk-test-001",
        "title": "Payment failure test",
        "description": "Card declined",
        "category": "billing",
        "priority": "high",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "billing"
    assert data["status"] == "open"
    assert data["id"].startswith("TKT-")

    db.delete(c)
    db.commit()


def test_list_tickets(client):
    resp = client.get("/api/v1/tickets")
    assert resp.status_code == 200
    assert "tickets" in resp.json()


def test_update_ticket_status(client, db):
    from app.models import Customer, Ticket, TicketStatus, TicketCategory, TicketPriority
    import uuid
    c = Customer(
        id="upd-test-001", name="Upd User", email="upd.user.unique@test.com",
        company="T", plan=CustomerPlan.STARTER, status=CustomerStatus.ACTIVE,
    )
    t = Ticket(
        id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        customer_id="upd-test-001",
        title="Test ticket",
        description="",
        category=TicketCategory.BILLING,
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
    )
    db.add(c)
    db.add(t)
    db.commit()

    resp = client.patch(f"/api/v1/tickets/{t.id}", json={
        "status": "resolved",
        "resolution": "Fixed by test",
        "successful_step": "Did the test thing",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"

    db.delete(t)
    db.delete(c)
    db.commit()


def test_get_ticket_not_found(client):
    resp = client.get("/api/v1/tickets/TKT-NOTEXIST")
    assert resp.status_code == 404
