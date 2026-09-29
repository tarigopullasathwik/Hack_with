"""
Customer management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database.db import get_db
from app.models import Customer, CustomerPlan, CustomerStatus
from app import hindsight as mem

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
def list_customers(db: Session = Depends(get_db)):
    """List all customers."""
    customers = db.query(Customer).order_by(Customer.name).all()
    return {"customers": [c.to_dict() for c in customers], "count": len(customers)}


@router.get("/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get a single customer profile."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.to_dict()


class CustomerCreate(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    plan: str = "starter"
    browser: Optional[str] = None
    operating_system: Optional[str] = None
    product_version: Optional[str] = None


@router.post("")
def create_customer(req: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer and initialise their Hindsight memory bank."""
    import uuid

    # Check for duplicate email
    existing = db.query(Customer).filter(Customer.email == req.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        plan = CustomerPlan(req.plan)
    except Exception:
        plan = CustomerPlan.STARTER

    customer = Customer(
        id=f"cust-{uuid.uuid4().hex[:8]}",
        name=req.name,
        email=req.email,
        company=req.company,
        plan=plan,
        status=CustomerStatus.ACTIVE,
        browser=req.browser,
        operating_system=req.operating_system,
        product_version=req.product_version,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    # Initialise Hindsight memory bank
    mem.create_bank(customer.id, customer.name, str(plan))

    return customer.to_dict()
