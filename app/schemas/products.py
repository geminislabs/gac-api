from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CatalogProductOut(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CatalogProductCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class CatalogProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
