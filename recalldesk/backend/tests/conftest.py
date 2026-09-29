"""
Test fixtures for RecallDesk.
"""
import pytest
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_recalldesk.db")
os.environ.setdefault("LLM_API_KEY", "sk-test-key")
os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("HINDSIGHT_EMBEDDED", "false")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, get_db
from app.main import app
from app.models import Customer, CustomerPlan, CustomerStatus
from app import hindsight as mem


TEST_DB_URL = "sqlite:///./test_recalldesk.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    mem.seed_demo_memories()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    db = TestSessionLocal()
    yield db
    db.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer(db):
    customer = Customer(
        id="test-cust-001",
        name="Test User",
        email="test@example.com",
        company="Test Corp",
        plan=CustomerPlan.BUSINESS,
        status=CustomerStatus.ACTIVE,
        browser="Chrome",
        operating_system="Windows",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    yield customer
    db.delete(customer)
    db.commit()
