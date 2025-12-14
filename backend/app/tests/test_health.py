"""Tests for health-related endpoints."""

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_db
from app.main import app


def test_health_echo() -> None:
    """POST /health/echo echoes the message back."""
    client = TestClient(app)

    payload = {"message": "hello"}
    response = client.post("/health/echo", json=payload)

    assert response.status_code == 200
    assert response.json() == payload


@pytest.fixture()
async def override_db_session() -> AsyncSession:
    """Provide an in-memory SQLite session for health/db tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture()
async def async_client(override_db_session: AsyncSession):
    """Async client with get_db overridden to use in-memory SQLite."""
    async def _override_get_db() -> AsyncSession:
        yield override_db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_health_db(async_client: AsyncClient) -> None:
    """GET /health/db returns healthy with in-memory DB."""
    response = await async_client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "database"


@pytest.mark.asyncio
async def test_health_ready(async_client: AsyncClient) -> None:
    """GET /health/ready returns ready with in-memory DB."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
