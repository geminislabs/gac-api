from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: UUID
    exp: int
    type: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    roles: List[str] = []

    class Config:
        from_attributes = True


class PasswordUpdate(BaseModel):
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
