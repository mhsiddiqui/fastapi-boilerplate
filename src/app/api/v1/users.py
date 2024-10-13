from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...crud.crud_users import crud_users
from ...schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(tags=["Account"], prefix="/account")


@router.post("/users/", response_model=UserRead, status_code=201)
async def write_user(
        request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead:
    if await user.is_valid(crud_users, db):
        user = await user.create(crud_users, db)
        return UserRead(**user.serialize())


@router.get("/users/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    return current_user


@router.put("/users/me/", response_model=UserRead)
async def update_user(
        request: Request, data: Annotated[UserUpdate, Form()],
        current_user: Annotated[UserRead, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead:
    if await data.is_valid(crud_users, db):
        _user = await data.update(crud_users, db, username=current_user.get('username'))
        updated_user = await crud_users.get(db, username=current_user.get('username'))
        return UserRead(**updated_user)
