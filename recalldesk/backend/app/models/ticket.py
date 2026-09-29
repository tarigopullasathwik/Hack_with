"""
Support ticket model.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database.db import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, enum.Enum):
    LOGIN = "login"
    BILLING = "billing"
    SUBSCRIPTION = "subscription"
    INTEGRATION = "integration"
    NOTIFICATIONS = "notifications"
    FILE_SYNC = "file_sync"
    PERMISSIONS = "permissions"
    API = "api"
    ACCOUNT = "account"
    OTHER = "other"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(64), primary_key=True)
    customer_id = Column(String(64), ForeignKey("customers.id"), nullable=False)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(SAEnum(TicketCategory), default=TicketCategory.OTHER)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(SAEnum(TicketPriority), default=TicketPriority.MEDIUM)

    # Resolution tracking
    resolution = Column(Text)
    resolution_steps = Column(Text)  # JSON list of steps tried
    failed_steps = Column(Text)      # JSON list of steps that failed
    successful_step = Column(Text)

    # Escalation
    escalated_to = Column(String(255))
    escalation_reason = Column(Text)
    handoff_summary = Column(Text)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True))

    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "priority": self.priority,
            "resolution": self.resolution,
            "resolution_steps": self.resolution_steps,
            "failed_steps": self.failed_steps,
            "successful_step": self.successful_step,
            "escalated_to": self.escalated_to,
            "escalation_reason": self.escalation_reason,
            "handoff_summary": self.handoff_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
