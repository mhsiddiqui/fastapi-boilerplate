from uuid import UUID

from sqlalchemy import or_, select
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed

from src.core.db.database import async_session_factory
from src.core.security import verify_password
from src.models.user import User

SESSION_KEY = "admin_user_id"


class AdminAuthProvider(AuthProvider):
    """Session-based auth for the admin UI.

    Reuses the ``User`` model and bcrypt verifier. Only ``is_active`` superusers
    are allowed in. The login form's "username" field accepts either email or
    username. Authenticated user id lives in the Starlette session, scoped to
    the admin path by ``SessionMiddleware``.
    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        async with async_session_factory() as db:
            result = await db.execute(
                select(User).where(or_(User.email == username, User.username == username))
            )
            user = result.scalar_one_or_none()

        if user is None or not verify_password(password, user.password):
            raise LoginFailed("Invalid credentials")
        if not user.is_active:
            raise LoginFailed("Inactive user")
        if not user.is_superuser:
            raise LoginFailed("Not authorized to access admin")

        request.session[SESSION_KEY] = str(user.id)
        return response

    async def is_authenticated(self, request: Request) -> bool:
        raw_id = request.session.get(SESSION_KEY)
        if not raw_id:
            return False
        try:
            user_id = UUID(raw_id)
        except ValueError:
            return False

        async with async_session_factory() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

        if user is None or not user.is_active or not user.is_superuser:
            return False

        request.state.user = user
        return True

    def get_admin_user(self, request: Request) -> AdminUser:
        user: User = request.state.user
        return AdminUser(username=user.username)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
