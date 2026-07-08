"""Fixtures compartidas para tests de gac-api (sin base de datos real)."""

import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bootstrap_env import bootstrap_test_runtime

bootstrap_test_runtime()

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_client_id() -> str:
    return str(uuid4())
