from typing import Annotated, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.users import User
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    stmt = (
        select(User)
        .options(selectinload(User.roles))
        .where(User.user_id == token_data.sub)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # 403 (no 404) para no confundir con "ruta inexistente" en logs y proxies.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def require_roles(allowed_roles: List[str]):
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]):
        user_roles = [role.name for role in current_user.roles]
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return current_user

    return role_checker
