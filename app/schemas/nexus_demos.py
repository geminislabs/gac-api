from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class NexusDemoCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    recipient_email: EmailStr
    scenario: str = Field(default="normal", max_length=32)
    notes: Optional[str] = None

    # Tope de 14 días al crear. Extender después es barato y reversible; una
    # demo de 90 días es un cliente que nunca decide.
    ttl_hours: int = Field(default=168, ge=1, le=336)


class NexusDemoUpdate(BaseModel):
    notes: Optional[str] = None


class NexusDemoExtend(BaseModel):
    ttl_hours: int = Field(ge=1, le=336)


class NexusDemoState(BaseModel):
    """Ciclo de vida, tal y como lo reporta el gate del entorno de demo.

    Es None cuando el gate no responde: se distingue a propósito de "no existe",
    para que la interfaz pueda decir "no se pudo consultar" en vez de pintar una
    demo viva como si estuviera muerta.
    """

    status: str
    scenario: Optional[str] = None
    invite_email: Optional[str] = None
    invites_issued: int = 0
    invite_expires_at_unix: Optional[int] = None
    redeemed_at_unix: Optional[int] = None
    expires_at_unix: Optional[int] = None
    ended_at_unix: Optional[int] = None


class NexusDemoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    demo_id: UUID
    tenant_id: str
    company_name: str
    recipient_email: str
    notes: Optional[str] = None
    scenario: str
    ttl_hours: int
    created_by: UUID
    created_by_name: Optional[str] = None
    created_at: Optional[datetime] = None

    state: Optional[NexusDemoState] = None


class NexusDemoCreated(BaseModel):
    """Respuesta de la creación. Es la ÚNICA vez que se ve el código.

    El gate guarda solo su hash, así que no es recuperable: si se pierde, hay
    que reemitir. No se persiste ni se registra en logs en ningún punto.
    """

    demo: NexusDemoResponse
    access_url: str
    otp: str
    otp_expires_in_seconds: Optional[int] = None
