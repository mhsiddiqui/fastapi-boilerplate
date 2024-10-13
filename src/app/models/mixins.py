import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass, DeclarativeBase, declared_attr


class UUIDMixin(object):
    @declared_attr
    def uuid(self):
        return Column(
            UUID, primary_key=True, default=uuid_pkg.uuid4, server_default=text("gen_random_uuid()")
        )


class TimestampMixin(object):
    @declared_attr
    def created(self) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    @declared_attr
    def modified(self) ->  Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), default=None)


class SoftDeleteMixin(object):
    @declared_attr
    def deleted_at(self) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), default=None)

    @declared_attr
    def is_deleted(self) -> Mapped[bool]:
        return mapped_column(default=False, index=True)

