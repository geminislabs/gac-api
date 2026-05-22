"""Tests unitarios para dependencias de autenticación y roles."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.deps import require_roles


def _user_with_roles(*role_names: str):
    roles = [SimpleNamespace(name=n) for n in role_names]
    return SimpleNamespace(
        user_id=uuid4(),
        email="u@test.com",
        roles=roles,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_require_roles_allows_admin():
    checker = require_roles(["admin"])
    user = _user_with_roles("admin")
    result = await checker(current_user=user)
    assert result is user


@pytest.mark.asyncio
async def test_require_roles_denies_user_without_admin():
    checker = require_roles(["admin"])
    user = _user_with_roles("user")
    with pytest.raises(HTTPException) as exc:
        await checker(current_user=user)
    assert exc.value.status_code == 403
    assert "permissions" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_require_roles_denies_empty_roles():
    checker = require_roles(["admin"])
    user = _user_with_roles()
    with pytest.raises(HTTPException) as exc:
        await checker(current_user=user)
    assert exc.value.status_code == 403
