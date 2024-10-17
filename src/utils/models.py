import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class UUIDMixin:
    @declared_attr
    def uuid(self):
        return Column(UUID, primary_key=True, default=uuid_pkg.uuid4, server_default=text("gen_random_uuid()"))


class TimestampMixin:
    @declared_attr
    def created(self) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    @declared_attr
    def modified(self) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), default=None)


class SoftDeleteMixin:
    @declared_attr
    def deleted_at(self) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), default=None)

    @declared_attr
    def is_deleted(self) -> Mapped[bool]:
        return mapped_column(default=False, index=True)
