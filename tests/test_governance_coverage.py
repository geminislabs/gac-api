"""Tests unitarios adicionales para alcanzar el umbral de cobertura de gobernanza."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jose import jwt
from starlette.requests import Request

from app.api.deps import get_current_user
from app.core import paseto as paseto_module
from app.core.config import settings
from app.core.paseto import (
    create_app_token,
    decode_app_token,
    decode_service_token,
    refresh_app_token,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.users import Role, User
from app.schemas.roles import RoleCreate
from app.schemas.users import UserCreate, UserUpdate
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.services.user_service import UserService


@pytest.mark.unit
class TestSecurityHelpers:
    def test_password_hash_and_verify(self):
        hashed = get_password_hash("secure-password-123")
        assert hashed != "secure-password-123"
        assert verify_password("secure-password-123", hashed)
        assert not verify_password("wrong-password", hashed)

    def test_create_access_token_default_expiry(self):
        user_id = uuid4()
        token = create_access_token(subject=user_id)
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_create_tokens_with_custom_delta(self):
        user_id = uuid4()
        access = create_access_token(
            subject=user_id, expires_delta=timedelta(minutes=10)
        )
        refresh = create_refresh_token(subject=user_id, expires_delta=timedelta(days=1))
        access_payload = jwt.decode(
            access, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        refresh_payload = jwt.decode(
            refresh, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"


@pytest.mark.unit
class TestPasetoHelpers:
    def test_create_and_decode_app_token_roundtrip(self):
        user_id = uuid4()
        token = create_app_token(user_id, app_name="gac", expires_in_minutes=5)
        payload = decode_app_token(token)
        assert payload["internal_id"] == str(user_id)
        assert payload["service"] == "gac"
        assert payload["role"] == "GAC_ADMIN"

    def test_refresh_app_token(self):
        user_id = uuid4()
        original = create_app_token(user_id)
        refreshed = refresh_app_token(original, app_name="gac")
        payload = decode_app_token(refreshed)
        assert payload["internal_id"] == str(user_id)

    def test_decode_app_token_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_app_token("not-a-valid-paseto-token")

    def test_decode_app_token_expired_raises(self):
        user_id = uuid4()
        past = datetime(2020, 1, 1, tzinfo=timezone.utc)

        class _FixedDatetime:
            @classmethod
            def now(cls, tz=None):
                return past

        with patch.object(paseto_module, "datetime") as mock_dt:
            mock_dt.now.return_value = past
            mock_dt.fromisoformat = datetime.fromisoformat
            mock_dt.side_effect = lambda *a, **k: datetime(*a, **k)
            token = create_app_token(user_id, expires_in_minutes=-60)

        with pytest.raises(ValueError, match="expired"):
            decode_app_token(token)

    def test_secret_key_padding_and_truncation(self, monkeypatch):
        short_key = base64.b64encode(b"short").decode()
        monkeypatch.setenv("PASETO_SECRET_KEY", short_key)
        from importlib import reload

        import app.core.config as config_module

        reload(config_module)
        reload(paseto_module)

        user_id = uuid4()
        token = paseto_module.create_app_token(user_id)
        payload = paseto_module.decode_app_token(token)
        assert payload["internal_id"] == str(user_id)

        long_raw = b"x" * 48
        long_key = base64.b64encode(long_raw).decode()
        monkeypatch.setenv("PASETO_SECRET_KEY", long_key)
        reload(config_module)
        reload(paseto_module)
        token2 = paseto_module.create_app_token(user_id)
        assert paseto_module.decode_app_token(token2)["internal_id"] == str(user_id)

    def test_decode_service_token_valid_scopes(self):
        user_id = uuid4()
        token = create_app_token(user_id, app_name="gac")
        payload = decode_service_token(token)
        assert payload is not None
        assert payload.get("service") == "gac"

    def test_decode_service_token_required_service_and_role(self):
        user_id = uuid4()
        token = create_app_token(user_id, app_name="gac")
        assert decode_service_token(token, required_service="gac") is not None
        assert decode_service_token(token, required_service="other") is None
        assert decode_service_token(token, required_role="GAC_ADMIN") is not None
        assert decode_service_token(token, required_role="OTHER") is None

    def test_decode_service_token_expired_returns_none(self):
        user_id = uuid4()
        past = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with patch.object(paseto_module, "datetime") as mock_dt:
            mock_dt.now.return_value = past
            mock_dt.fromisoformat = datetime.fromisoformat
            token = create_app_token(user_id, expires_in_minutes=-10)
        assert decode_service_token(token) is None

    def test_decode_service_token_invalid_scope_returns_none(self, monkeypatch):
        user_id = uuid4()
        token = create_app_token(user_id)
        payload = decode_app_token(token)
        payload["scope"] = "invalid-scope"
        payload["service"] = "other"

        monkeypatch.setattr(
            paseto_module,
            "decode_app_token",
            lambda _t: payload,
        )
        with patch.object(paseto_module.pyseto, "decode") as mock_decode:
            mock_decode.return_value = MagicMock(
                payload=__import__("json").dumps(payload).encode()
            )
            assert decode_service_token(token) is None

    def test_refresh_app_token_invalid_raises(self):
        with pytest.raises(ValueError, match="Cannot refresh token"):
            refresh_app_token("invalid-token")


@pytest.mark.unit
class TestDepsGetCurrentUser:
    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        user_id = uuid4()
        token = create_access_token(subject=user_id)
        role = SimpleNamespace(name="admin")
        user = SimpleNamespace(
            user_id=user_id,
            email="u@test.com",
            roles=[role],
            is_active=True,
        )

        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db.execute.return_value = result

        current = await get_current_user(token=token, db=db)
        assert current is user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_jwt(self):
        db = AsyncMock()
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token="not-a-jwt", db=db)
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        user_id = uuid4()
        token = create_access_token(subject=user_id)
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result

        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=token, db=db)
        assert exc.value.status_code == 403
        assert "not found" in str(exc.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_current_user_inactive(self):
        user_id = uuid4()
        token = create_access_token(subject=user_id)
        user = SimpleNamespace(
            user_id=user_id,
            email="u@test.com",
            roles=[],
            is_active=False,
        )
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db.execute.return_value = result

        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=token, db=db)
        assert exc.value.status_code == 400
        assert "inactive" in str(exc.value.detail).lower()


@pytest.mark.unit
class TestAuthService:
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session_sqlite):
        password = "password-123"
        user = User(
            email="auth@test.example",
            password_hash=get_password_hash(password),
            full_name="Auth User",
            is_active=True,
        )
        db_session_sqlite.add(user)
        await db_session_sqlite.commit()

        service = AuthService(db_session_sqlite)
        token = await service.authenticate_user("auth@test.example", password)
        assert token is not None
        assert token.token_type == "bearer"
        assert token.access_token
        assert token.refresh_token

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session_sqlite):
        user = User(
            email="wrong@test.example",
            password_hash=get_password_hash("correct"),
            is_active=True,
        )
        db_session_sqlite.add(user)
        await db_session_sqlite.commit()

        service = AuthService(db_session_sqlite)
        assert await service.authenticate_user("wrong@test.example", "bad") is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, db_session_sqlite):
        user = User(
            email="inactive@test.example",
            password_hash=get_password_hash("password-123"),
            is_active=False,
        )
        db_session_sqlite.add(user)
        await db_session_sqlite.commit()

        service = AuthService(db_session_sqlite)
        assert (
            await service.authenticate_user("inactive@test.example", "password-123")
            is None
        )

    @pytest.mark.asyncio
    async def test_refresh_token_flow(self, db_session_sqlite):
        user = User(
            email="refresh@test.example",
            password_hash=get_password_hash("password-123"),
            is_active=True,
        )
        db_session_sqlite.add(user)
        await db_session_sqlite.commit()
        await db_session_sqlite.refresh(user)

        refresh = create_refresh_token(subject=user.user_id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db_session_sqlite.execute = AsyncMock(return_value=result)

        service = AuthService(db_session_sqlite)
        new_tokens = await service.refresh_token(refresh)
        assert new_tokens is not None
        assert new_tokens.access_token

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_type(self, db_session_sqlite):
        user_id = uuid4()
        access = create_access_token(subject=user_id)
        service = AuthService(db_session_sqlite)
        assert await service.refresh_token(access) is None

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_jwt(self, db_session_sqlite):
        service = AuthService(db_session_sqlite)
        assert await service.refresh_token("not-a-jwt") is None


@pytest.mark.unit
class TestUserAndRoleServices:
    @pytest.mark.asyncio
    async def test_user_service_create_user(self, db_session_sqlite):
        role = Role(name="admin")
        db_session_sqlite.add(role)
        await db_session_sqlite.commit()

        service = UserService(db_session_sqlite)
        created = await service.create_user(
            UserCreate(
                email="user@test.example",
                password="password-123",
                full_name="Test User",
                roles=["admin"],
            )
        )
        assert created.email == "user@test.example"
        assert created.user_id is not None

        users = await service.get_users()
        assert len(users) >= 1

    @pytest.mark.asyncio
    async def test_user_service_update_delete_with_mock(self):
        user_id = uuid4()
        user = User(
            user_id=user_id,
            email="mock@test.example",
            password_hash="hash",
            full_name="Before",
            is_active=True,
        )
        user.roles = []

        db = AsyncMock()

        async def _execute_side_effect(stmt):
            result = MagicMock()
            result.scalar_one_or_none.return_value = user
            result.scalars.return_value.all.return_value = []
            return result

        db.execute = AsyncMock(side_effect=_execute_side_effect)
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        service = UserService(db)
        updated = await service.update_user(
            user_id, UserUpdate(full_name="After", is_active=False)
        )
        assert updated is not None
        assert updated.full_name == "After"
        assert await service.change_password(user_id, "new-password-99")
        assert await service.delete_user(user_id)

    @pytest.mark.asyncio
    async def test_user_service_get_user_missing(self):
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=result)
        service = UserService(db)
        assert await service.get_user(uuid4()) is None
        assert await service.update_user(uuid4(), UserUpdate(full_name="x")) is None
        assert not await service.change_password(uuid4(), "pw")
        assert not await service.delete_user(uuid4())

    @pytest.mark.asyncio
    async def test_user_service_duplicate_email(self, db_session_sqlite):
        service = UserService(db_session_sqlite)
        await service.create_user(
            UserCreate(email="dup@test.example", password="password-123")
        )
        with pytest.raises(ValueError, match="already registered"):
            await service.create_user(
                UserCreate(email="dup@test.example", password="password-123")
            )

    @pytest.mark.asyncio
    async def test_role_service_create_and_list(self, db_session_sqlite):
        service = RoleService(db_session_sqlite)
        role = await service.create_role(RoleCreate(name="operator"))
        roles = await service.get_roles()
        assert any(r.name == "operator" for r in roles)
        assert role.role_id is not None

        with pytest.raises(ValueError, match="already exists"):
            await service.create_role(RoleCreate(name="operator"))

    @pytest.mark.asyncio
    async def test_role_service_assign_with_mock(self):
        user_id = uuid4()
        role_id = uuid4()
        db = AsyncMock()
        exists_result = MagicMock()
        exists_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=exists_result)
        db.commit = AsyncMock()
        db.add = MagicMock()
        db.rollback = AsyncMock()

        service = RoleService(db)
        assert await service.assign_role_to_user(user_id, role_id)

        exists_result.scalar_one_or_none.return_value = MagicMock()
        assert await service.assign_role_to_user(user_id, role_id)

        delete_result = MagicMock()
        delete_result.rowcount = 1
        db.execute = AsyncMock(return_value=delete_result)
        assert await service.revoke_role_from_user(user_id, role_id)


@pytest.mark.unit
class TestMainExceptionHandlers:
    @pytest.mark.asyncio
    async def test_http_exception_handler_string_detail(self):
        from app.main import http_exception_handler

        scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
        request = Request(scope)
        exc = HTTPException(status_code=404, detail="Not found")
        response = await http_exception_handler(request, exc)
        assert response.status_code == 404
        body = __import__("json").loads(response.body)
        assert body["message"] == "Not found"
        assert body["error"] == "http_404"

    @pytest.mark.asyncio
    async def test_http_exception_handler_dict_detail(self):
        from app.main import http_exception_handler

        scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
        request = Request(scope)
        exc = HTTPException(status_code=400, detail={"code": "bad_request"})
        response = await http_exception_handler(request, exc)
        body = __import__("json").loads(response.body)
        assert body["detail"] == {"code": "bad_request"}

    def test_health_endpoint_metadata(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "gac-api"
        assert data["version"] == "1.0.0"
