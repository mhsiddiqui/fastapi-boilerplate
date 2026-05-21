from collections.abc import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.database import get_async_db
from src.core.setup import app


async def test_health_returns_ok(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok"}


async def test_health_returns_503_when_db_down(client: AsyncClient) -> None:
    """If the DB session raises, /health must surface 503 rather than 500."""

    class _BoomSession:
        async def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield _BoomSession()  # type: ignore[misc]

    previous = app.dependency_overrides.get(get_async_db)
    app.dependency_overrides[get_async_db] = _override
    try:
        r = await client.get("/health")
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_async_db, None)
        else:
            app.dependency_overrides[get_async_db] = previous

    assert r.status_code == 503
    body = r.json()
    assert body["detail"]["status"] == "degraded"
    assert body["detail"]["database"] == "down"
