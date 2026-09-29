"""Tests for customer creation and lookup."""
import pytest


def test_create_customer(client):
    resp = client.post("/api/v1/customers", json={
        "name": "Alice Test",
        "email": "alice.test.unique@example.com",
        "company": "Acme",
        "plan": "business",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Alice Test"
    assert data["plan"] == "business"
    assert "id" in data


def test_list_customers(client):
    resp = client.get("/api/v1/customers")
    assert resp.status_code == 200
    data = resp.json()
    assert "customers" in data
    assert isinstance(data["customers"], list)


def test_get_customer_not_found(client):
    resp = client.get("/api/v1/customers/nonexistent-id")
    assert resp.status_code == 404


def test_duplicate_email_rejected(client):
    email = "dup.test.x99@example.com"
    client.post("/api/v1/customers", json={"name": "A", "email": email})
    resp = client.post("/api/v1/customers", json={"name": "B", "email": email})
    assert resp.status_code == 409
