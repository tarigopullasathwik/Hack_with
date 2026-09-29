"""
Demo mode API endpoints — pre-built scenarios for hackathon judges.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from app.database.db import get_db
from app.models import DemoScenario, Customer, Ticket, Message
from app import hindsight as mem

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    """List all available demo scenarios."""
    scenarios = db.query(DemoScenario).order_by(DemoScenario.sort_order).all()
    result = []
    for s in scenarios:
        d = s.to_dict()
        # Include customer name
        customer = db.query(Customer).filter(Customer.id == s.customer_id).first()
        d["customer_name"] = customer.name if customer else "Unknown"
        d["customer_plan"] = customer.plan if customer else "unknown"
        result.append(d)
    return {"scenarios": result}


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Get a specific demo scenario."""
    scenario = db.query(DemoScenario).filter(DemoScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario.to_dict()


@router.get("/customers")
def get_demo_customers(db: Session = Depends(get_db)):
    """Get the featured demo customers with their ticket history."""
    demo_customer_ids = ["cust-001", "cust-002", "cust-004"]
    result = []
    for cid in demo_customer_ids:
        customer = db.query(Customer).filter(Customer.id == cid).first()
        if customer:
            tickets = (
                db.query(Ticket)
                .filter(Ticket.customer_id == cid)
                .order_by(Ticket.created_at.desc())
                .all()
            )
            d = customer.to_dict()
            d["tickets"] = [t.to_dict() for t in tickets]
            d["ticket_count"] = len(tickets)
            result.append(d)
    return {"customers": result}


@router.get("/memory-timeline/{customer_id}")
def get_memory_timeline(customer_id: str, db: Session = Depends(get_db)):
    """
    Build a memory timeline for a customer.
    Shows: ticket events + memory retain points + outcomes.
    """
    tickets = (
        db.query(Ticket)
        .filter(Ticket.customer_id == customer_id)
        .order_by(Ticket.created_at.asc())
        .all()
    )

    timeline = []
    for ticket in tickets:
        entry = {
            "date": ticket.created_at.strftime("%b %d, %Y") if ticket.created_at else "",
            "timestamp": ticket.created_at.isoformat() if ticket.created_at else "",
            "ticket_id": ticket.id,
            "title": ticket.title,
            "category": ticket.category,
            "status": ticket.status,
            "outcome": ticket.status,
            "successful_step": ticket.successful_step,
            "failed_steps": json.loads(ticket.failed_steps) if ticket.failed_steps else [],
            "resolution": ticket.resolution,
            "escalated": ticket.status == "escalated",
        }
        timeline.append(entry)

    # Also get Hindsight memories if available
    hindsight_memories = []
    if mem.is_available():
        result = mem.list_memories(customer_id, limit=20)
        if result["success"]:
            hindsight_memories = result["memories"]

    return {
        "customer_id": customer_id,
        "timeline": timeline,
        "hindsight_memories": hindsight_memories,
        "hindsight_available": mem.is_available(),
    }


@router.post("/compare/{customer_id}")
def before_after_compare(customer_id: str, body: dict, db: Session = Depends(get_db)):
    """
    Run the same message through both memory modes and return both responses.
    This powers the Before/After comparison panel.
    """
    from app.agents.support_agent import process_message
    import uuid

    message = body.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    session_id = str(uuid.uuid4())

    # Without memory
    without = process_message(
        db=db,
        customer_id=customer_id,
        session_id=session_id + "-no-mem",
        user_message=message,
        memory_mode="without_memory",
    )

    # With memory
    with_mem = process_message(
        db=db,
        customer_id=customer_id,
        session_id=session_id + "-mem",
        user_message=message,
        memory_mode="with_memory",
    )

    return {
        "message": message,
        "without_memory": {
            "response": without["response"],
            "memories_recalled": [],
            "memory_count": 0,
        },
        "with_memory": {
            "response": with_mem["response"],
            "memories_recalled": with_mem["memories_recalled"],
            "memory_count": with_mem["memory_count"],
        },
    }


@router.get("/stats")
def get_demo_stats(db: Session = Depends(get_db)):
    """Stats for the demo dashboard."""
    from app.models import Ticket, TicketStatus
    total_customers = db.query(Customer).count()
    total_tickets = db.query(Ticket).count()
    resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count()
    escalated = db.query(Ticket).filter(Ticket.status == TicketStatus.ESCALATED).count()
    total_messages = db.query(Message).count()

    return {
        "total_customers": total_customers,
        "total_tickets": total_tickets,
        "resolved_tickets": resolved,
        "escalated_tickets": escalated,
        "total_messages": total_messages,
        "hindsight_available": mem.is_available(),
        "hindsight_status": mem.get_status(),
    }
