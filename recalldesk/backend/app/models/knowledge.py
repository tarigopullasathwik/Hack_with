"""
Knowledge base article model.
"""
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from datetime import datetime, timezone
from app.database.db import Base
import enum


class ArticleCategory(str, enum.Enum):
    BILLING = "billing"
    LOGIN = "login"
    SSO = "sso"
    INTEGRATION = "integration"
    FILE_SYNC = "file_sync"
    PERMISSIONS = "permissions"
    SUBSCRIPTION = "subscription"
    NOTIFICATIONS = "notifications"
    API = "api"
    ACCOUNT = "account"


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(String(64), primary_key=True)
    title = Column(String(500), nullable=False)
    category = Column(SAEnum(ArticleCategory))
    content = Column(Text, nullable=False)
    tags = Column(Text)                      # comma-separated
    troubleshooting_steps = Column(Text)     # JSON list
    common_causes = Column(Text)             # JSON list
    escalation_triggers = Column(Text)       # JSON list

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "content": self.content,
            "tags": self.tags,
            "troubleshooting_steps": self.troubleshooting_steps,
            "common_causes": self.common_causes,
            "escalation_triggers": self.escalation_triggers,
        }
