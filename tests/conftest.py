"""Fixtures compartidas para tests de gac-api (sin base de datos real)."""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Variables mínimas antes de importar settings / app
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DB_SCHEME", "gac")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-for-unit-tests")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("PASETO_SECRET_KEY", "dGVzdC1wYXNldG8tc2VjcmV0LWtleS0zMmJ5dGVz")

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_client_id() -> str:
    return str(uuid4())
