"""Tests de ejemplo con fixtures SQLite en memoria."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Role, User


@pytest.mark.asyncio
async def test_create_role_sqlite(db_session_sqlite: AsyncSession):
    role = Role(name="admin")
    db_session_sqlite.add(role)
    await db_session_sqlite.commit()
    await db_session_sqlite.refresh(role)

    assert role.role_id is not None
    assert role.name == "admin"


@pytest.mark.asyncio
async def test_create_user_sqlite(db_session_sqlite: AsyncSession):
    user = User(
        email="sqlite@test.example",
        password_hash="hashed",
        full_name="SQLite User",
        is_active=True,
    )
    db_session_sqlite.add(user)
    await db_session_sqlite.commit()
    await db_session_sqlite.refresh(user)

    result = await db_session_sqlite.execute(
        select(User).where(User.email == "sqlite@test.example")
    )
    row = result.scalar_one()
    assert row.full_name == "SQLite User"


def test_client_sqlite_health(client_sqlite):
    response = client_sqlite.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
