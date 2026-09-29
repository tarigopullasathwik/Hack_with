"""
Demo scenario model — pre-built scenarios for hackathon judges.
"""
from sqlalchemy import Column, String, DateTime, Text, Integer
from datetime import datetime, timezone
from app.database.db import Base


class DemoScenario(Base):
    __tablename__ = "demo_scenarios"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    customer_id = Column(String(64), nullable=False)
    scenario_type = Column(String(100))  # e.g. "recurring_billing", "integration_failure", "escalation"
    sort_order = Column(Integer, default=0)

    # Pre-scripted interaction turns stored as JSON
    turns = Column(Text)  # JSON list of {role, content, delay_ms}

    # Memory checkpoints: what should be recalled at each turn
    memory_checkpoints = Column(Text)  # JSON

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "customer_id": self.customer_id,
            "scenario_type": self.scenario_type,
            "sort_order": self.sort_order,
            "turns": self.turns,
            "memory_checkpoints": self.memory_checkpoints,
        }
