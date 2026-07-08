from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.schemas.roles import RoleCreate, RoleResponse
from app.services.role_service import RoleService

router = APIRouter()


# Only admins can manage roles
@router.post(
    "/roles",
    response_model=ResponseModel[RoleResponse],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def create_role(
    role_in: RoleCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = RoleService(db)
    try:
        role = await service.create_role(role_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ResponseModel(message="Role created successfully", data=role)


@router.get(
    "/roles",
    response_model=ResponseModel[List[RoleResponse]],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def get_roles(db: Annotated[AsyncSession, Depends(get_db)]):
    service = RoleService(db)
    roles = await service.get_roles()
    return ResponseModel(message="Roles retrieved successfully", data=roles)


@router.post(
    "/users/{user_id}/roles/{role_id}",
    response_model=ResponseModel[bool],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def assign_role(
    user_id: UUID, role_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = RoleService(db)
    success = await service.assign_role_to_user(user_id, role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign role")
    return ResponseModel(message="Role assigned successfully", data=True)


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    response_model=ResponseModel[bool],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def revoke_role(
    user_id: UUID, role_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = RoleService(db)
    success = await service.revoke_role_from_user(user_id, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return ResponseModel(message="Role revoked successfully", data=True)
