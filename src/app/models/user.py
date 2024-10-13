from datetime import UTC, datetime
from typing import Optional

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import DateTime, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column

from .mixins import TimestampMixin, SoftDeleteMixin
from ..core.db.database import Base
from ..core.storage import get_storage_class


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False
    )

    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String)

    profile_image: Mapped[Optional[str]] =  mapped_column(
        FileType(storage=get_storage_class(path="profile-image")), nullable=True, default=None
    )
    is_active: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    @classmethod
    async def exists(cls, db, *filters):
        query = select(User).where(*filters).limit(1)
        result = await db.execute(query)
        return result.first() is not None

    def serialize(self) -> dict:
        return self.__dict__