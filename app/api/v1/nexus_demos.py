"""Accesos de demo de Nexus, para la consola comercial.

Permisos:

- Ver el listado y el detalle: ``admin`` o ``vendedor``. Sin filtrar por
  creador — un admin tiene que ver lo que generan los vendedores.
- Crear y extender: ``admin`` o ``vendedor``.
- Resetear y dar de baja: solo el vendedor que la creó, o un admin. Destruyen
  el entorno del cliente de otro.
"""

from typing import Annotated, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core import nexus_demo as nexus
from app.core.config import settings
from app.core.database import get_db
from app.models.nexus_demos import NexusDemo
from app.models.users import User
from app.schemas.common import ResponseModel
from app.schemas.nexus_demos import (
    NexusDemoCreate,
    NexusDemoCreated,
    NexusDemoExtend,
    NexusDemoResponse,
    NexusDemoState,
    NexusDemoUpdate,
)
from app.services.nexus_demo_service import NexusDemoService

router = APIRouter()

DEMO_ROLES = ["admin", "vendedor"]


def _is_admin(user: User) -> bool:
    return any(role.name == "admin" for role in user.roles)


def _require_owner_or_admin(demo: NexusDemo, user: User) -> None:
    if _is_admin(user) or demo.created_by == user.user_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Solo el vendedor que generó la demo o un admin pueden hacer esto",
    )


def _to_response(demo: NexusDemo, state: Optional[dict[str, Any]]) -> NexusDemoResponse:
    response = NexusDemoResponse.model_validate(demo)
    response.created_by_name = getattr(demo.creator, "full_name", None) or getattr(
        demo.creator, "email", None
    )
    if state:
        response.state = NexusDemoState(**state)
    return response


def _guard_configured() -> None:
    from app.core.config import missing_nexus_demo_config

    missing = missing_nexus_demo_config()
    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Integración con el entorno de demo sin configurar: {', '.join(missing)}",
        )


def _nexus_error(exc: nexus.NexusDemoError) -> HTTPException:
    # 401/404 del gate NO se propagan tal cual: un 401 hacia el navegador haría
    # que el front cerrara la sesión del vendedor, cuando el problema es entre
    # gac-api y el entorno de demo.
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.post(
    "/nexus-demos",
    response_model=ResponseModel[NexusDemoCreated],
    status_code=status.HTTP_201_CREATED,
)
async def create_nexus_demo(
    payload: NexusDemoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
):
    """Genera un acceso de demo. Devuelve el código UNA sola vez."""
    _guard_configured()
    service = NexusDemoService(db)
    try:
        demo, invite = await service.create(payload, current_user.user_id)
    except nexus.NexusDemoError as exc:
        raise _nexus_error(exc)

    base = (settings.NEXUS_DEMO_OPS_URL or "").rstrip("/")
    return ResponseModel(
        message="Acceso de demo generado",
        data=NexusDemoCreated(
            demo=_to_response(demo, None),
            access_url=f"{base}/access",
            otp=invite.get("otp", ""),
            otp_expires_in_seconds=invite.get("ttl_seconds"),
            provisioning=invite.get("provisioning", True),
        ),
    )


@router.get("/nexus-demos", response_model=ResponseModel[List[NexusDemoResponse]])
async def list_nexus_demos(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    service = NexusDemoService(db)
    demos = await service.list(skip=skip, limit=limit)
    states = await service.states_for(demos)
    return ResponseModel(
        message="Accesos de demo obtenidos",
        data=[_to_response(d, states.get(d.tenant_id)) for d in demos],
    )


@router.get("/nexus-demos/{demo_id}", response_model=ResponseModel[NexusDemoResponse])
async def get_nexus_demo(
    demo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
):
    service = NexusDemoService(db)
    demo = await service.get(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Acceso de demo no encontrado")
    state = await service.state_for(demo)
    return ResponseModel(
        message="Acceso de demo obtenido", data=_to_response(demo, state)
    )


@router.patch("/nexus-demos/{demo_id}", response_model=ResponseModel[NexusDemoResponse])
async def update_nexus_demo(
    demo_id: UUID,
    payload: NexusDemoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
):
    """Solo las notas comerciales. El resto de la ficha es historial."""
    service = NexusDemoService(db)
    demo = await service.get(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Acceso de demo no encontrado")
    demo = await service.update_notes(demo, payload.notes)
    return ResponseModel(message="Notas actualizadas", data=_to_response(demo, None))


@router.post(
    "/nexus-demos/{demo_id}/extend", response_model=ResponseModel[NexusDemoResponse]
)
async def extend_nexus_demo(
    demo_id: UUID,
    payload: NexusDemoExtend,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
):
    """Extiende la vigencia.

    Solo funciona mientras el workflow siga vivo: una vez expirada, no hay a
    quién enviarle la señal y hay que generar una demo nueva.
    """
    _guard_configured()
    service = NexusDemoService(db)
    demo = await service.get(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Acceso de demo no encontrado")
    try:
        await nexus.signal_extend(demo.tenant_id, payload.ttl_hours)
        state = await service.state_for(demo)
    except nexus.NexusDemoError as exc:
        raise _nexus_error(exc)
    return ResponseModel(message="Vigencia extendida", data=_to_response(demo, state))


@router.post(
    "/nexus-demos/{demo_id}/reset", response_model=ResponseModel[NexusDemoResponse]
)
async def reset_nexus_demo(
    demo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
):
    """Devuelve la flota simulada a su estado inicial. El código sigue valiendo."""
    _guard_configured()
    service = NexusDemoService(db)
    demo = await service.get(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Acceso de demo no encontrado")
    _require_owner_or_admin(demo, current_user)
    try:
        await nexus.signal_reset(demo.tenant_id)
        state = await service.state_for(demo)
    except nexus.NexusDemoError as exc:
        raise _nexus_error(exc)
    return ResponseModel(
        message="Datos de la demo reseteados", data=_to_response(demo, state)
    )


@router.post(
    "/nexus-demos/{demo_id}/revoke", response_model=ResponseModel[NexusDemoResponse]
)
async def revoke_nexus_demo(
    demo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(DEMO_ROLES))],
):
    """Destruye el entorno ahora. No se puede deshacer.

    La ficha comercial NO se borra: es el historial de a quién se le demostró
    qué y cuándo, y sobrevive al entorno.
    """
    _guard_configured()
    service = NexusDemoService(db)
    demo = await service.get(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Acceso de demo no encontrado")
    _require_owner_or_admin(demo, current_user)
    try:
        await nexus.signal_teardown(demo.tenant_id)
        state = await service.state_for(demo)
    except nexus.NexusDemoError as exc:
        raise _nexus_error(exc)
    return ResponseModel(message="Demo dada de baja", data=_to_response(demo, state))
