import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=64)]
    name: Annotated[str, Field(min_length=1, max_length=120)]
    password: Annotated[str, Field(min_length=8, max_length=128)]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    username: str
    name: str
    is_active: bool
    is_superuser: bool
    created: datetime
    modified: datetime | None


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    username: Annotated[str | None, Field(default=None, min_length=3, max_length=64)]
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=120)]
