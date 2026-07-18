from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrderItemBase(BaseModel):
    device_id: Optional[UUID] = None
    product_key: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(ge=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    item_id: UUID
    order_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    client_id: UUID
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderResponse(OrderBase):
    order_id: UUID
    created_by: Optional[UUID] = None
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
