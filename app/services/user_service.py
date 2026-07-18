from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.models.users import Role, User, UserRole
from app.schemas.users import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: UserCreate) -> User:
        # Check email
        stmt = select(User).where(User.email == user_in.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Create user
        user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=user_in.is_active,
        )
        self.db.add(user)
        await self.db.flush()  # Get ID

        # Assign roles
        if user_in.roles:
            await self._sync_roles(user.user_id, user_in.roles)

        await self.db.commit()
        await self.db.refresh(user, attribute_names=["roles"])
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(User).options(selectinload(User.roles)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user(self, user_id: UUID) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, user_in: UserUpdate) -> Optional[User]:
        user = await self.get_user(user_id)
        if not user:
            return None

        if user_in.full_name is not None:
            user.full_name = user_in.full_name
        if user_in.is_active is not None:
            user.is_active = user_in.is_active

        if user_in.roles is not None:
            await self._sync_roles(user.user_id, user_in.roles)

        await self.db.commit()
        await self.db.refresh(user, attribute_names=["roles"])
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False

        user.is_active = False
        await self.db.commit()
        return True

    async def change_password(self, user_id: UUID, new_password: str) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False

        user.password_hash = get_password_hash(new_password)
        await self.db.commit()
        return True

    async def _sync_roles(self, user_id: UUID, role_names: List[str]):
        # Clear existing roles
        stmt = delete(UserRole).where(UserRole.user_id == user_id)
        await self.db.execute(stmt)

        if not role_names:
            return

        # Find role IDs
        stmt = select(Role).where(Role.name.in_(role_names))
        result = await self.db.execute(stmt)
        roles = result.scalars().all()

        # Add new roles
        for role in roles:
            user_role = UserRole(user_id=user_id, role_id=role.role_id)
            self.db.add(user_role)
