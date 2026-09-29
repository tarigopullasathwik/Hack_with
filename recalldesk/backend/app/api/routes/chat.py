"""
Chat API endpoints — main agent interaction surface.
"""
import uuid
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.agents.support_agent import process_message
from app.models import Message, MessageRole

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    customer_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    memory_mode: str = "with_memory"   # "with_memory" | "without_memory"
    active_ticket_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    memories_recalled: list
    memory_count: int
    memory_retained: bool
    tool_calls: list
    activity: list
    outcome: str
    ticket_id: Optional[str]
    escalated: bool
    handoff_summary: Optional[str]
    hindsight_status: dict


@router.post("", response_model=ChatResponse)
def send_message(req: ChatRequest, db: Session = Depends(get_db)):
    """Send a message to the RecallDesk support agent."""
    session_id = req.session_id or str(uuid.uuid4())

    result = process_message(
        db=db,
        customer_id=req.customer_id,
        session_id=session_id,
        user_message=req.message,
        memory_mode=req.memory_mode,
        active_ticket_id=req.active_ticket_id,
    )

    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        memories_recalled=result["memories_recalled"],
        memory_count=result["memory_count"],
        memory_retained=result["memory_retained"],
        tool_calls=result["tool_calls"],
        activity=result["activity"],
        outcome=result["outcome"],
        ticket_id=result.get("ticket_id"),
        escalated=result["escalated"],
        handoff_summary=result.get("handoff_summary"),
        hindsight_status=result["hindsight_status"],
    )


@router.get("/history/{customer_id}/{session_id}")
def get_chat_history(
    customer_id: str,
    session_id: str,
    db: Session = Depends(get_db),
):
    """Get conversation history for a session."""
    messages = (
        db.query(Message)
        .filter(
            Message.customer_id == customer_id,
            Message.session_id == session_id,
        )
        .order_by(Message.created_at.asc())
        .all()
    )
    return {"messages": [m.to_dict() for m in messages], "count": len(messages)}


@router.get("/sessions/{customer_id}")
def get_sessions(customer_id: str, db: Session = Depends(get_db)):
    """Get all session IDs for a customer."""
    sessions = (
        db.query(Message.session_id)
        .filter(Message.customer_id == customer_id)
        .distinct()
        .all()
    )
    return {"sessions": [s[0] for s in sessions]}
