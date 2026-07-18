from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.core.database import get_db
from app.schemas.auth import PasswordUpdate
from app.schemas.common import ResponseModel
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/users",
    response_model=ResponseModel[UserResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin"]))],
)
async def create_user(
    user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = UserService(db)
    try:
        user = await service.create_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Convert to response
    roles = [role.name for role in user.roles]
    response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=roles,
    )
    return ResponseModel(message="User created successfully", data=response)


@router.get(
    "/users",
    response_model=ResponseModel[List[UserResponse]],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    service = UserService(db)
    users = await service.get_users(skip, limit)

    response_data = []
    for user in users:
        roles = [role.name for role in user.roles]
        response_data.append(
            UserResponse(
                user_id=user.user_id,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                roles=roles,
            )
        )

    return ResponseModel(message="Users retrieved successfully", data=response_data)


@router.get(
    "/users/{user_id}",
    response_model=ResponseModel[UserResponse],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def get_user(user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    roles = [role.name for role in user.roles]
    response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=roles,
    )
    return ResponseModel(message="User retrieved successfully", data=response)


@router.patch(
    "/users/{user_id}",
    response_model=ResponseModel[UserResponse],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def update_user(
    user_id: UUID, user_in: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = UserService(db)
    user = await service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    roles = [role.name for role in user.roles]
    response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=roles,
    )
    return ResponseModel(message="User updated successfully", data=response)


@router.delete(
    "/users/{user_id}",
    response_model=ResponseModel[bool],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def delete_user(user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(message="User deactivated successfully", data=True)


@router.patch(
    "/users/{user_id}/password",
    response_model=ResponseModel[bool],
    dependencies=[Depends(require_roles(["admin"]))],
)
async def reset_user_password(
    user_id: UUID,
    password_in: PasswordUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Resetea la contraseña de un usuario (solo admin).
    No requiere la contraseña actual del usuario.
    """
    service = UserService(db)
    success = await service.change_password(user_id, password_in.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(message="Password reset successfully", data=True)
