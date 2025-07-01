from datetime import datetime
from typing import Annotated, Union

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.utils.constants import Messages
from src.utils.exceptions.http_exceptions import CustomValidationException
from src.utils.schemas import BaseSchema


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class UserRead(BaseModel):
    id: int

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class UserCreate(UserBase, BaseSchema):
    model_config = ConfigDict(extra="forbid")
    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]

    async def validate_email(self, email, crud, db):
        email_row = await crud.exists(db=db, email=email)
        if email_row:
            raise CustomValidationException(message=Messages.EMAIL_ALREADY_EXISTS, field="email")
        return email

    async def validate_username(self, username, crud, db):
        username_row = await crud.exists(db=db, username=username)
        if username_row:
            raise CustomValidationException(message=Messages.USERNAME_ALREADY_EXISTS, field="username")
        return username

    async def create(self, crud, db):
        from src.utils.authentication import get_password_hash

        user_data = self.model_dump()
        user_data["password"] = get_password_hash(password=user_data["password"])
        created_user: UserRead = await crud.create(db=db, object=UserCreate(**user_data))
        return created_user


class UserCreateInternal(UserBase):
    password: str


class UserUpdate(BaseSchema):
    model_config = ConfigDict(extra="forbid")
    name: Annotated[Union[str, None], Form()] = None

    async def update(self, crud, db, **kwargs):
        data = self.model_dump()
        updated: UserRead = await crud.update(db=db, object=data, **kwargs)
        return updated


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
