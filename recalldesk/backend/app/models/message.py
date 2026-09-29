"""
Conversation message model.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database.db import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True)
    customer_id = Column(String(64), ForeignKey("customers.id"), nullable=False)
    ticket_id = Column(String(64), ForeignKey("tickets.id"), nullable=True)
    session_id = Column(String(64), nullable=False)

    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Memory metadata
    memories_recalled = Column(Text)   # JSON: list of recalled memory snippets
    memories_retained = Column(Text)   # JSON: what was retained after this msg
    memory_count = Column(String(10))  # number of memories recalled

    # Tool calls made during this message
    tool_calls = Column(Text)          # JSON list

    # Memory mode for before/after demo
    memory_mode = Column(String(20), default="with_memory")  # "with_memory" | "without_memory"

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    customer = relationship("Customer", back_populates="messages")
    ticket = relationship("Ticket", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "ticket_id": self.ticket_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "memories_recalled": self.memories_recalled,
            "memories_retained": self.memories_retained,
            "memory_count": self.memory_count,
            "tool_calls": self.tool_calls,
            "memory_mode": self.memory_mode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
