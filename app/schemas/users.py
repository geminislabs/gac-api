from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    is_active: bool = True
    roles: List[str] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None


class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    roles: List[str] = []

    class Config:
        from_attributes = True
