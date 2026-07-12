from __future__ import annotations

import os
from collections.abc import AsyncIterator

os.environ["RAOS_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RAOS_AUTO_CREATE_TABLES"] = "false"
os.environ["RAOS_AUTO_PROCESS_CAPTURES"] = "false"
os.environ["RAOS_OWNER_EMAIL"] = "ryan@example.com"
os.environ["RAOS_OWNER_PASSWORD"] = "test-password"
os.environ["RAOS_JWT_SECRET"] = "test-secret-that-is-long-enough-for-tests"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app

engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestSession = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_db() -> AsyncIterator[AsyncSession]:
    async with TestSession() as session:
        yield session


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_db_session] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    async with TestSession() as session:
        yield session
