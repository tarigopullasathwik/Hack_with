"""
Support ticket API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database.db import get_db
from app.models import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.tools.support_tools import create_ticket, update_ticket, escalate_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def list_tickets(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List tickets with optional filters."""
    q = db.query(Ticket)
    if customer_id:
        q = q.filter(Ticket.customer_id == customer_id)
    if status:
        try:
            q = q.filter(Ticket.status == TicketStatus(status))
        except Exception:
            pass
    tickets = q.order_by(Ticket.created_at.desc()).limit(limit).all()
    return {"tickets": [t.to_dict() for t in tickets], "count": len(tickets)}


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Get a single ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket.to_dict()


class TicketCreateRequest(BaseModel):
    customer_id: str
    title: str
    description: str = ""
    category: str = "other"
    priority: str = "medium"


@router.post("")
def create_ticket_endpoint(req: TicketCreateRequest, db: Session = Depends(get_db)):
    result = create_ticket(
        db, req.customer_id, req.title, req.description, req.category, req.priority
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create ticket"))
    return result["ticket"]


class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None
    resolution: Optional[str] = None
    successful_step: Optional[str] = None
    failed_steps: Optional[list[str]] = None


@router.patch("/{ticket_id}")
def update_ticket_endpoint(
    ticket_id: str, req: TicketUpdateRequest, db: Session = Depends(get_db)
):
    result = update_ticket(
        db, ticket_id,
        status=req.status,
        resolution=req.resolution,
        successful_step=req.successful_step,
        failed_steps=req.failed_steps,
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
    return result["ticket"]


class EscalateRequest(BaseModel):
    reason: str
    history_summary: str = ""
    what_worked: str = ""
    what_failed: str = ""
    environment: str = ""


@router.post("/{ticket_id}/escalate")
def escalate_ticket_endpoint(
    ticket_id: str, req: EscalateRequest, db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    result = escalate_ticket(
        db,
        ticket_id=ticket_id,
        customer_id=ticket.customer_id,
        reason=req.reason,
        customer_name=ticket.customer.name if ticket.customer else "",
        history_summary=req.history_summary,
        what_worked=req.what_worked,
        what_failed=req.what_failed,
        environment=req.environment,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Escalation failed"))
    return result
