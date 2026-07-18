from typing import List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Role, UserRole
from app.schemas.roles import RoleCreate


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role_in: RoleCreate) -> Role:
        role = Role(name=role_in.name)
        self.db.add(role)
        try:
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Role already exists")

    async def get_roles(self) -> List[Role]:
        stmt = select(Role)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> bool:
        # Check if exists
        stmt = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            return True  # Already assigned

        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        try:
            await self.db.commit()
            return True
        except IntegrityError:
            await self.db.rollback()
            return False

    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        stmt = delete(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
