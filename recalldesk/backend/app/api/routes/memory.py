"""
Memory API endpoints — expose Hindsight operations directly for the Memory Panel UI.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app import hindsight as mem

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/status")
def memory_status():
    """Get Hindsight availability status."""
    return mem.get_status()


@router.get("/{customer_id}")
def list_customer_memories(
    customer_id: str,
    memory_type: Optional[str] = None,
    limit: int = 50,
):
    """List all memories stored for a customer."""
    result = mem.list_memories(customer_id, memory_type=memory_type, limit=limit)
    if not result["success"] and not mem.is_available():
        return {
            "memories": [],
            "count": 0,
            "hindsight_available": False,
            "message": "Memory unavailable for this request.",
        }
    return {
        "memories": result["memories"],
        "count": result.get("count", 0),
        "hindsight_available": mem.is_available(),
    }


class RecallRequest(BaseModel):
    query: str
    budget: str = "mid"
    types: Optional[list[str]] = None


@router.post("/{customer_id}/recall")
def recall_memories(customer_id: str, req: RecallRequest):
    """Explicitly recall memories for a customer given a query."""
    if not mem.is_available():
        return {
            "memories": [],
            "count": 0,
            "hindsight_available": False,
            "message": "Memory unavailable for this request.",
        }
    result = mem.recall(
        customer_id=customer_id,
        query=req.query,
        budget=req.budget,
        types=req.types,
    )
    return {
        **result,
        "hindsight_available": True,
    }


class RetainRequest(BaseModel):
    content: str
    context: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/{customer_id}/retain")
def retain_memory(customer_id: str, req: RetainRequest):
    """Manually retain a memory for a customer (admin/demo use)."""
    if not mem.is_available():
        raise HTTPException(status_code=503, detail="Hindsight memory unavailable")
    result = mem.retain(
        customer_id=customer_id,
        content=req.content,
        context=req.context,
        metadata=req.metadata,
    )
    return result


class ReflectRequest(BaseModel):
    query: str
    budget: str = "mid"
    context: Optional[str] = None


@router.post("/{customer_id}/reflect")
def reflect_on_memories(customer_id: str, req: ReflectRequest):
    """Deep reflection over a customer's memory bank."""
    if not mem.is_available():
        raise HTTPException(status_code=503, detail="Hindsight memory unavailable")
    result = mem.reflect(
        customer_id=customer_id,
        query=req.query,
        budget=req.budget,
        context=req.context,
    )
    return result
