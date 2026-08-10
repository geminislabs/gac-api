from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NexusDemo(Base):
    """Ficha comercial de un acceso de demo de Nexus.

    Guarda solo lo comercial: quién la generó, para qué cliente y con qué notas.
    El ciclo de vida —si sigue viva, cuándo la aceptó el cliente, cuándo caduca—
    NO se replica aquí: lo responde el gate del demo en
    ``GET /internal/tenants``, y se cruza por ``tenant_id`` al leer.

    Duplicar el estado sería la forma más rápida de acabar con dos verdades
    sobre si una demo sigue activa, y la de GAC sería siempre la desactualizada.
    """

    __tablename__ = "nexus_demos"
    __table_args__ = {"schema": "gac"}

    demo_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )

    # Identificador del tenant en el entorno de demo. Es la única llave que une
    # esta fila con el estado que vive en la base del gate.
    tenant_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    scenario: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")

    # Vigencia solicitada al crear. Se guarda para poder mostrar qué se pidió,
    # aunque la fecha real de expiración la manda el workflow de Temporal.
    ttl_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=168)

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("gac.users.user_id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(
        server_default=func.now(), nullable=True
    )

    creator: Mapped["User"] = relationship("User", lazy="joined")  # noqa: F821
