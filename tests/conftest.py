"""Test fixtures.

Tests run against a dedicated Postgres database. Override the name via the
``POSTGRES_DB_TEST`` env var; otherwise ``<POSTGRES_DB>_test`` is used. You
are responsible for creating that database before running the suite::

    createdb -h $POSTGRES_SERVER -U $POSTGRES_USER ${POSTGRES_DB}_test

Schema is created via ``Base.metadata.create_all`` per session (not Alembic),
and every row is wiped between tests so test order doesn't matter.
"""

import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.db.base import Base
from src.core.db.database import get_async_db
from src.core.rate_limit import limiter
from src.core.settings import settings
from src.core.setup import app
from src.models import user as _user_models  # noqa: F401  - register with Base.metadata

# Bypass slowapi during tests so rate limits don't fight us.
limiter.enabled = False

_TEST_DB_NAME = os.environ.get("POSTGRES_DB_TEST", f"{settings.POSTGRES_DB}_test")
_TEST_DATABASE_URL = (
    f"{settings.POSTGRES_ASYNC_PREFIX}{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{_TEST_DB_NAME}"
)

_engine = create_async_engine(_TEST_DATABASE_URL, echo=False, future=True)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_database() -> AsyncGenerator[None, None]:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _truncate_tables() -> AsyncGenerator[None, None]:
    """Wipe rows between tests (after each test runs)."""
    yield
    async with _engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """An ``AsyncClient`` bound to the FastAPI app with the test session
    plugged into the ``get_async_db`` dependency."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_async_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
