from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    order_id: Optional[UUID] = None
    client_id: UUID
    amount: Decimal = Field(gt=0)
    method: str
    transaction_ref: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    payment_id: UUID
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
