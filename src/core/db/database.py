from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from src.core.db.base import Base
from src.core.settings import settings

__all__ = ["Base", "async_engine", "async_session_factory", "get_async_db", "get_sync_db"]


async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.POSTGRES_ECHO,
    future=True,
    pool_pre_ping=settings.POSTGRES_POOL_PRE_PING,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a per-request async SQLAlchemy session."""
    async with async_session_factory() as session:
        yield session


def get_sync_db() -> Session:
    """Sync session for management commands and Alembic helpers."""
    sync_engine = create_engine(
        settings.SYNC_DATABASE_URL,
        echo=settings.POSTGRES_ECHO,
        future=True,
        pool_pre_ping=settings.POSTGRES_POOL_PRE_PING,
    )
    return Session(sync_engine)
