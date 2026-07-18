from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class ShipmentBase(BaseModel):
    order_id: UUID
    client_id: UUID
    shipping_carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    address: Optional[Dict[str, Any]] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdateStatus(BaseModel):
    status: str


class ShipmentResponse(ShipmentBase):
    shipment_id: UUID
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
