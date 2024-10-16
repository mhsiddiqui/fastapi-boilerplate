from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from fastcrud.exceptions.http_exceptions import UnauthorizedException, ForbiddenException
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.account.crud import crud_users
from core.db.database import async_get_db
from core.logger import logging
from .authentication import oauth2_scheme, verify_token
from ..utils.constants import Messages

logger = logging.getLogger(__name__)


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any] | None:
    token_data = await verify_token(token, db)
    if token_data is None:
        raise UnauthorizedException(Messages.NOT_AUTHENTICATED)

    filters = {'db': db, 'is_deleted': False, 'is_active': True}

    if "@" in token_data.username_or_email:
        filters['email'] = token_data.username_or_email
    else:
        filters['username'] = token_data.username_or_email

    user = await crud_users.get(**filters)

    if user:
        return user

    raise UnauthorizedException(Messages.NOT_AUTHENTICATED)


async def get_optional_user(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict | None:
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exc:
        if http_exc.status_code != 401:
            logger.error(f"Unexpected HTTPException in get_optional_user: {http_exc.detail}")
        return None

    except Exception as exc:
        logger.error(f"Unexpected error in get_optional_user: {exc}")
        return None


async def get_current_superuser(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    if not current_user["is_superuser"]:
        raise ForbiddenException("You do not have enough privileges.")

    return current_user
