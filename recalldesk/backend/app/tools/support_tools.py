"""
Support tools available to the RecallDesk agent.

Each tool is a plain function that returns a dict.
The agent calls these during reasoning and their results are shown in the
Activity Feed on the frontend.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Customer, Ticket, TicketStatus, TicketPriority, TicketCategory, KnowledgeArticle, Message
from app import hindsight as mem

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1: Customer lookup
# ─────────────────────────────────────────────────────────────────────────────

def lookup_customer(db: Session, customer_id: str) -> dict:
    """Look up a customer profile by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"found": False, "error": f"Customer {customer_id} not found"}
    return {"found": True, "customer": customer.to_dict()}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2: Ticket history
# ─────────────────────────────────────────────────────────────────────────────

def get_ticket_history(db: Session, customer_id: str, limit: int = 10) -> dict:
    """Retrieve recent tickets for a customer."""
    tickets = (
        db.query(Ticket)
        .filter(Ticket.customer_id == customer_id)
        .order_by(Ticket.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "tickets": [t.to_dict() for t in tickets],
        "count": len(tickets),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3: Subscription lookup
# ─────────────────────────────────────────────────────────────────────────────

def lookup_subscription(db: Session, customer_id: str) -> dict:
    """Return subscription/billing context for a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"found": False, "error": "Customer not found"}

    # Synthetic subscription data derived from customer plan
    plan_features = {
        "free":       {"seats": 5,  "storage_gb": 10, "api_calls_day": 1000,  "sso": False},
        "starter":    {"seats": 15, "storage_gb": 50, "api_calls_day": 10000, "sso": False},
        "business":   {"seats": 50, "storage_gb": 500,"api_calls_day": 100000,"sso": True},
        "enterprise": {"seats": -1, "storage_gb": -1, "api_calls_day": -1,    "sso": True},
    }
    features = plan_features.get(customer.plan, plan_features["starter"])

    return {
        "found": True,
        "customer_id": customer_id,
        "plan": customer.plan,
        "status": customer.status,
        "features": features,
        "billing_status": "current",  # synthetic — could be "past_due", "suspended"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4: Billing status
# ─────────────────────────────────────────────────────────────────────────────

def get_billing_status(db: Session, customer_id: str) -> dict:
    """Return billing status details."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"found": False, "error": "Customer not found"}

    # Check for recent billing-related tickets
    billing_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.customer_id == customer_id,
            Ticket.category == TicketCategory.BILLING,
        )
        .order_by(Ticket.created_at.desc())
        .limit(3)
        .all()
    )

    return {
        "found": True,
        "customer_id": customer_id,
        "plan": customer.plan,
        "account_status": customer.status,
        "recent_billing_issues": [t.to_dict() for t in billing_tickets],
        "payment_method_on_file": True,   # synthetic
        "billing_profile_complete": True,  # synthetic
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 5: Knowledge base lookup
# ─────────────────────────────────────────────────────────────────────────────

def search_knowledge_base(db: Session, query: str, category: Optional[str] = None) -> dict:
    """Search knowledge articles matching the query."""
    q = db.query(KnowledgeArticle)
    if category:
        try:
            cat = ArticleCategory(category)  # noqa: F821
            q = q.filter(KnowledgeArticle.category == cat)
        except Exception:
            pass

    # Simple keyword search across title + content
    articles = q.all()
    query_lower = query.lower()
    scored = []
    for a in articles:
        score = 0
        if query_lower in (a.title or "").lower():
            score += 3
        if query_lower in (a.content or "").lower():
            score += 1
        tags = (a.tags or "").lower()
        for word in query_lower.split():
            if word in tags:
                score += 2
        if score > 0:
            scored.append((score, a))

    scored.sort(key=lambda x: -x[0])
    return {
        "articles": [a.to_dict() for _, a in scored[:5]],
        "count": len(scored),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 6: Create ticket
# ─────────────────────────────────────────────────────────────────────────────

def create_ticket(
    db: Session,
    customer_id: str,
    title: str,
    description: str,
    category: str = "other",
    priority: str = "medium",
) -> dict:
    """Create a new support ticket."""
    try:
        cat = TicketCategory(category)
    except Exception:
        cat = TicketCategory.OTHER
    try:
        pri = TicketPriority(priority)
    except Exception:
        pri = TicketPriority.MEDIUM

    ticket = Ticket(
        id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        customer_id=customer_id,
        title=title,
        description=description,
        category=cat,
        priority=pri,
        status=TicketStatus.OPEN,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    logger.info(f"Created ticket {ticket.id} for customer {customer_id}")
    return {"success": True, "ticket": ticket.to_dict()}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 7: Update ticket
# ─────────────────────────────────────────────────────────────────────────────

def update_ticket(
    db: Session,
    ticket_id: str,
    status: Optional[str] = None,
    resolution: Optional[str] = None,
    successful_step: Optional[str] = None,
    failed_steps: Optional[list] = None,
) -> dict:
    """Update an existing ticket's status or resolution."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return {"success": False, "error": f"Ticket {ticket_id} not found"}

    if status:
        try:
            ticket.status = TicketStatus(status)
            if status == "resolved":
                ticket.resolved_at = datetime.now(timezone.utc)
        except Exception:
            pass
    if resolution:
        ticket.resolution = resolution
    if successful_step:
        ticket.successful_step = successful_step
    if failed_steps is not None:
        ticket.failed_steps = json.dumps(failed_steps)

    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return {"success": True, "ticket": ticket.to_dict()}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 8: Escalate ticket
# ─────────────────────────────────────────────────────────────────────────────

def escalate_ticket(
    db: Session,
    ticket_id: str,
    customer_id: str,
    reason: str,
    customer_name: str,
    history_summary: str,
    what_worked: str = "",
    what_failed: str = "",
    environment: str = "",
) -> dict:
    """
    Escalate to human support.
    Generates a handoff summary containing all relevant context.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return {"success": False, "error": f"Ticket {ticket_id} not found"}

    handoff = f"""
═══════════════════════════════════════════════════════
HUMAN HANDOFF SUMMARY — RecallDesk
Ticket: {ticket_id}
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
═══════════════════════════════════════════════════════

CUSTOMER
  Name:    {customer_name}
  Company: see profile
  Plan:    {ticket.customer.plan if ticket.customer else 'N/A'}
  Environment: {environment}

CURRENT ISSUE
  {ticket.title}
  {ticket.description or ''}

REASON FOR ESCALATION
  {reason}

INTERACTION HISTORY
  {history_summary}

WHAT WAS TRIED
  Failed steps:  {what_failed or 'None recorded'}
  Working fixes: {what_worked or 'None recorded'}

RECOMMENDED NEXT ACTION
  Review billing/account admin panel for account-level issues.
  Do NOT ask the customer to repeat troubleshooting steps listed above.
  Refer to previous successful resolution when applicable.

═══════════════════════════════════════════════════════
""".strip()

    ticket.status = TicketStatus.ESCALATED
    ticket.escalation_reason = reason
    ticket.handoff_summary = handoff
    ticket.escalated_to = "human_support_team"
    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "ticket": ticket.to_dict(),
        "handoff_summary": handoff,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 9: Recall customer history from Hindsight
# ─────────────────────────────────────────────────────────────────────────────

def recall_customer_memory(customer_id: str, query: str) -> dict:
    """
    Recall relevant memories about the customer from Hindsight.
    This is explicitly marked as a Hindsight operation.
    """
    result = mem.recall(customer_id=customer_id, query=query, budget="mid")
    return {
        "source": "hindsight",
        "customer_id": customer_id,
        **result,
    }
