"""Fixtures compartidas para tests de gac-api."""

import sys
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bootstrap_env import bootstrap_test_runtime

bootstrap_test_runtime()

from sqlite_metadata import ensure_sqlite_metadata  # noqa: E402

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

SQLITE_TEST_URL = "sqlite+aiosqlite:///:memory:"

sqlite_test_engine = create_async_engine(
    SQLITE_TEST_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SqliteTestSessionLocal = async_sessionmaker(
    sqlite_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def _clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_client_id() -> str:
    return str(uuid4())


@pytest_asyncio.fixture
async def db_session_sqlite() -> AsyncGenerator[AsyncSession, None]:
    """Sesión SQLite en memoria para tests nuevos (sin PostgreSQL)."""
    ensure_sqlite_metadata(Base.metadata)

    async with sqlite_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SqliteTestSessionLocal() as session:
        yield session
        await session.rollback()

    async with sqlite_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db_sqlite(db_session_sqlite: AsyncSession):
    async def _get_db_override():
        yield db_session_sqlite

    return _get_db_override


@pytest.fixture
def client_sqlite(override_get_db_sqlite) -> Generator[TestClient, None, None]:
    """TestClient con get_db apuntando a SQLite en memoria."""
    app.dependency_overrides[get_db] = override_get_db_sqlite

    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client_sqlite(override_get_db_sqlite) -> AsyncGenerator:
    from httpx import ASGITransport, AsyncClient

    app.dependency_overrides[get_db] = override_get_db_sqlite

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
