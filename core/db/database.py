from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session, sessionmaker

from ..settings import settings


class Base(DeclarativeBase, MappedAsDataclass):
    @classmethod
    def query(cls):
        return select(cls)

    def serialize(self) -> dict:
        return self.__dict__


DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
POSTGRES_SYNC_PREFIX = settings.POSTGRES_SYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"
SYNC_DATABASE_URL = f"{POSTGRES_SYNC_PREFIX}{DATABASE_URI}"

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

local_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncSession:
    async_session = local_session
    async with async_session() as db:
        yield db


def get_sync_db():
    engine = create_engine(SYNC_DATABASE_URL, echo=False)
    return Session(engine)
