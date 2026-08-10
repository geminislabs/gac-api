"""Lógica de los accesos de demo de Nexus.

Reparto de responsabilidades: esta base guarda lo comercial (quién, para quién,
con qué notas) y el entorno de demo guarda el ciclo de vida. Al leer se cruzan
por ``tenant_id``; nunca se copia el estado a esta base.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import nexus_demo as nexus
from app.core.config import settings
from app.models.nexus_demos import NexusDemo
from app.schemas.nexus_demos import NexusDemoCreate

logger = logging.getLogger(__name__)


class NexusDemoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, payload: NexusDemoCreate, created_by: UUID
    ) -> tuple[NexusDemo, dict[str, Any]]:
        """Crea la ficha, emite la invitación y arranca el aprovisionamiento.

        Orden deliberado:

        1. La invitación primero, porque devuelve el código y es lo que el
           vendedor necesita en pantalla. Es un INSERT en el gate y responde
           en milisegundos.
        2. El workflow después. Tarda minutos, así que si fallara ya tendríamos
           el código: la demo queda "pendiente de aprovisionar", que es un
           estado recuperable, en vez de perder el código emitido.

        Lo que NO se hace: reintentar la creación de la invitación. No es
        idempotente — un reintento ciego acuña un segundo código y el vendedor
        acaba dictando el que ya no vale.
        """
        tenant_id = nexus.generate_tenant_id()
        ttl_hours = payload.ttl_hours or settings.NEXUS_DEMO_DEFAULT_TTL_HOURS

        invite = await nexus.create_otp_invite(
            tenant_id=tenant_id,
            scenario=payload.scenario,
            email=str(payload.recipient_email),
            ttl_hours=ttl_hours,
        )

        demo = NexusDemo(
            tenant_id=tenant_id,
            company_name=payload.company_name,
            recipient_email=str(payload.recipient_email),
            notes=payload.notes,
            scenario=payload.scenario,
            ttl_hours=ttl_hours,
            created_by=created_by,
        )
        self.db.add(demo)
        await self.db.commit()
        await self.db.refresh(demo)

        try:
            await nexus.start_demo_tenant(
                tenant_id=tenant_id,
                scenario=payload.scenario,
                email=str(payload.recipient_email),
                ttl_hours=ttl_hours,
            )
            provisioning = True
        except nexus.NexusDemoError as exc:
            # La ficha y el código ya existen y son válidos. Se informa, pero no
            # se tumba la operación: reaprovisionar es recuperable, reemitir el
            # código no lo es tanto.
            logger.warning(
                "demo %s: invitación emitida pero el aprovisionamiento falló: %s",
                tenant_id,
                exc,
            )
            provisioning = False

        invite = dict(invite or {})
        invite["provisioning"] = provisioning
        return demo, invite

    async def get(self, demo_id: UUID) -> Optional[NexusDemo]:
        result = await self.db.execute(
            select(NexusDemo).where(NexusDemo.demo_id == demo_id)
        )
        return result.unique().scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[NexusDemo]:
        """Todas las demos, sin filtrar por creador.

        Es una consola interna: los admins necesitan ver lo que generan los
        vendedores, y a un vendedor le sirve saber que un compañero ya tiene
        una demo abierta con la misma empresa. Cada fila lleva quién la creó.
        """
        result = await self.db.execute(
            select(NexusDemo)
            .order_by(NexusDemo.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.unique().scalars().all()

    async def update_notes(self, demo: NexusDemo, notes: Optional[str]) -> NexusDemo:
        demo.notes = notes
        await self.db.commit()
        await self.db.refresh(demo)
        return demo

    async def states_for(self, demos: Sequence[NexusDemo]) -> dict[str, dict[str, Any]]:
        """Estado de un lote de demos, en una sola llamada al gate.

        Si el gate no responde se devuelve un mapa vacío y las fichas salen sin
        estado. Es deliberado: que la consola siga listando lo comercial cuando
        el entorno de demo está caído es mejor que un error que oculta todo.
        """
        if not demos:
            return {}
        try:
            return await nexus.list_tenant_states(limit=max(len(demos), 50))
        except nexus.NexusDemoError as exc:
            logger.warning("no se pudo consultar el estado de las demos: %s", exc)
            return {}

    async def state_for(self, demo: NexusDemo) -> Optional[dict[str, Any]]:
        try:
            return await nexus.get_tenant_state(demo.tenant_id)
        except nexus.NexusDemoError as exc:
            logger.warning("no se pudo consultar la demo %s: %s", demo.tenant_id, exc)
            return None
