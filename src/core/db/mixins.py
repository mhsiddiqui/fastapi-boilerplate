from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


def _utc_now() -> datetime:
    return datetime.now(UTC)


class TimeStampedModel(MappedAsDataclass, kw_only=True):
    """Mixin that adds ``created`` and ``modified`` timezone-aware timestamps.

    ``created`` is populated once on insert. ``modified`` is set automatically
    on every UPDATE via SQLAlchemy's ``onupdate`` hook.

    Extends ``MappedAsDataclass`` (kw_only) so its columns participate in the
    dataclass machinery of any ``Base`` subclass that inherits this mixin.
    """

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=_utc_now,
    )
    modified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=_utc_now,
    )


class SoftDeleteMixin(MappedAsDataclass, kw_only=True):
    """Mixin adding logical-deletion columns.

    ``is_deleted`` is indexed so the common ``WHERE is_deleted = false`` filter
    is cheap. ``deleted_at`` is the audit timestamp. Use the ``soft_delete()``
    helper to flip both atomically::

        user.soft_delete()
        await db.commit()

    Reads must filter explicitly — this mixin does not install a global filter
    on the session.
    """

    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
    )

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = _utc_now()
