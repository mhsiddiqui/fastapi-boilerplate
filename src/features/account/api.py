from typing import Annotated

from fastapi import Depends, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.database import async_get_db
from core.easy_router.base_cbv import BaseView

from ...utils.authentication import get_current_user
from .crud import crud_users
from .schemas import UserCreate, UserRead, UserUpdate


async def write_user(
    request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead:
    if await user.is_valid(crud_users, db):
        user = await user.create(crud_users, db)
        return UserRead(**user.serialize())


class CurrentUserView(BaseView):
    async def get(self, request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
        return current_user

    async def put(
        self,
        request: Request,
        data: Annotated[UserUpdate, Form()],
        current_user: Annotated[UserRead, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)],
    ) -> UserRead:
        if await data.is_valid(crud_users, db):
            await data.update(crud_users, db, username=current_user.get("username"))
            updated_user = await crud_users.get(db, username=current_user.get("username"))
            return UserRead(**updated_user)
