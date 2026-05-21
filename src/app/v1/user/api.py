from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.database import get_async_db
from src.core.pagination import Page, PaginationParams, paginate
from src.core.security import get_current_user, hash_password
from src.models.user import User
from src.app.v1.user.schemas import UserRead, UserRegister, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_async_db)) -> User:
    existing = await db.execute(
        select(User.id).where(or_(User.email == payload.email, User.username == payload.username))
    )
    if existing.first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already registered")

    user = User(
        email=payload.email,
        username=payload.username,
        name=payload.name,
        password=hash_password(payload.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        ) from exc
    await db.refresh(user)
    return user


@router.get("", response_model=Page[UserRead])
async def list_users(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(get_current_user),
    params: PaginationParams = Depends(),
) -> Page[UserRead]:
    stmt = select(User).order_by(User.created.desc())
    return await paginate(request, db, stmt, UserRead, params)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this user")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return user

    collision_clauses = []
    new_email = updates.get("email")
    new_username = updates.get("username")
    if new_email and new_email != user.email:
        collision_clauses.append(User.email == new_email)
    if new_username and new_username != user.username:
        collision_clauses.append(User.username == new_username)
    if collision_clauses:
        clash = await db.execute(select(User.id).where(or_(*collision_clauses), User.id != user.id))
        if clash.first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already taken")

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already taken",
        ) from exc
    await db.refresh(user)
    return user
