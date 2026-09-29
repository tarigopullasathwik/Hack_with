"""Tests for knowledge base endpoints."""


def test_list_knowledge_articles(client):
    resp = client.get("/api/v1/knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert "articles" in data
    assert data["count"] >= 0  # May be 0 if seed not run but endpoint works


def test_search_knowledge_base(client):
    resp = client.get("/api/v1/knowledge/search?q=payment")
    assert resp.status_code == 200
    data = resp.json()
    assert "articles" in data


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "RecallDesk"
