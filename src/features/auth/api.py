from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastcrud.exceptions.http_exceptions import UnauthorizedException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.database import async_get_db
from src.utils.authentication import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from src.utils.authentication import blacklist_token, oauth2_scheme
from core.settings import settings
from .schemas import Token

router = APIRouter(tags=["Authentication"], prefix='/auth')


# @router.post("/login/", response_model=Token)
async def login_for_access_token(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Token:
    user = await authenticate_user(username_or_email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise UnauthorizedException("Wrong username, email or password.")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
    )

    return Token(**{"access_token": access_token, "token_type": "bearer"})


# @router.post("/refresh/")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(async_get_db)) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing.")

    user_data = await verify_token(refresh_token, db)
    if not user_data:
        raise UnauthorizedException("Invalid refresh token.")

    new_access_token = await create_access_token(data={"sub": user_data.username_or_email})
    return Token(**{"access_token": new_access_token, "token_type": "bearer"})


@router.post("/logout")
async def logout(
        response: Response, access_token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(async_get_db)
) -> dict[str, str]:
    try:
        await blacklist_token(token=access_token, db=db)
        response.delete_cookie(key="refresh_token")

        return {"message": "Logged out successfully"}

    except JWTError:
        raise UnauthorizedException("Invalid token.")
