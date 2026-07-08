from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.auth import PasswordUpdate, RefreshTokenRequest, Token, UserResponse
from app.schemas.common import ResponseModel
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/auth/login", response_model=ResponseModel[Token])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    token = await service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return ResponseModel(message="Login successful", data=token)


@router.post("/auth/refresh", response_model=ResponseModel[Token])
async def refresh_token(
    payload: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Renueva el par de tokens a partir de un refresh token válido."""
    service = AuthService(db)
    token = await service.refresh_token(payload.refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return ResponseModel(message="Token refreshed successfully", data=token)


@router.get("/auth/me", response_model=ResponseModel[UserResponse])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    # Convert SQLAlchemy model to Pydantic schema manually or rely on from_attributes
    # UserResponse expects roles as list of strings
    roles = [role.name for role in current_user.roles]
    user_response = UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        roles=roles,
    )
    return ResponseModel(message="User profile retrieved", data=user_response)


@router.patch("/auth/password", response_model=ResponseModel[bool])
async def change_my_password(
    password_in: PasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Cambia la contraseña del usuario autenticado.
    No requiere la contraseña actual, solo estar autenticado.
    """
    service = UserService(db)
    success = await service.change_password(
        current_user.user_id, password_in.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password",
        )
    return ResponseModel(message="Password changed successfully", data=True)
