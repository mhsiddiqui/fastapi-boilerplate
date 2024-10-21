from typing import Optional

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.db.database import Base
from core.storage import get_storage_class
from src.utils.models import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String)

    profile_image: Mapped[Optional[str]] = mapped_column(
        FileType(storage=get_storage_class(path="profile-image")), nullable=True, default=None
    )
    is_active: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
