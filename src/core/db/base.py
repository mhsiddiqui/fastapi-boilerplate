from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    """Declarative base for all ORM models.

    Inherits ``MappedAsDataclass`` (with ``kw_only=True``) so subclasses behave
    as keyword-only dataclasses — column ordering across mixins and the model
    body does not matter, and all instantiation is explicit:

        user = User(email="x@y.z", username="x", name="X", password=h)

    Query with plain SQLAlchemy 2.0 idioms::

        result = await db.execute(select(User).where(User.email == "x@y.z"))
        user = result.scalar_one_or_none()
    """

    def serialize(self) -> dict:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
