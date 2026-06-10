from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_roles
from app.core.paseto import create_app_token, refresh_app_token
from app.models.users import User
from app.schemas.common import ResponseModel

router = APIRouter()


@router.post(
    "/internal/tokens/app",
    response_model=ResponseModel[str],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def generate_app_token(
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    """
    Genera un token PASETO para comunicación interna de aplicaciones.
    Solo accesible por usuarios con rol admin.

    El token expira en 5 minutos y contiene:
    - internal_id: UUID del usuario
    - service: "gac"
    - role: "GAC_ADMIN"
    - scope: "internal-gac-admin"
    """
    token = create_app_token(user_id=current_user.user_id, app_name="gac")
    return ResponseModel(message="Token generated successfully", data=token)


@router.post(
    "/internal/tokens/refresh",
    response_model=ResponseModel[str],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def refresh_app_token_endpoint(
    token: str,
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    """
    Refresca un token PASETO existente generando uno nuevo.
    Solo accesible por usuarios con rol admin.

    Args:
        token: Token PASETO existente a refrescar

    Returns:
        Nuevo token PASETO con expiración renovada
    """
    try:
        new_token = refresh_app_token(token, app_name="gac")
        return ResponseModel(message="Token refreshed successfully", data=new_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/internal/debug/user",
    response_model=ResponseModel[dict],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def debug_current_user(
    current_user: Annotated[User, Depends(require_roles(["admin"]))],
):
    """
    Endpoint de debugging para verificar información del usuario actual.
    Solo accesible por usuarios con rol admin.
    """
    roles = [role.name for role in current_user.roles]
    user_info = {
        "user_id": str(current_user.user_id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "roles": roles,
        "has_admin_role": "admin" in roles,
    }
    return ResponseModel(message="User debug info", data=user_info)
