"""
Customer model — stores profile, plan, and environment context.
"""
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database.db import Base


class CustomerPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CHURNED = "churned"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    company = Column(String(255))
    plan = Column(SAEnum(CustomerPlan), default=CustomerPlan.STARTER)
    status = Column(SAEnum(CustomerStatus), default=CustomerStatus.ACTIVE)

    # Environment context
    browser = Column(String(100))
    operating_system = Column(String(100))
    product_version = Column(String(50))
    workspace_size = Column(String(50))  # e.g., "12 members"

    # Notes / summary
    profile_notes = Column(Text)
    preferences = Column(Text)  # JSON string

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    tickets = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="customer", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "plan": self.plan,
            "status": self.status,
            "browser": self.browser,
            "operating_system": self.operating_system,
            "product_version": self.product_version,
            "workspace_size": self.workspace_size,
            "profile_notes": self.profile_notes,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
