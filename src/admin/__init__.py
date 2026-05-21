from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin

from src.admin.auth import AdminAuthProvider
from src.admin.views import UserView
from src.core.db.database import async_engine
from src.core.settings import settings
from src.models.user import User

admin = Admin(
    engine=async_engine,
    title=f"{settings.APP_NAME} Admin",
    base_url="/admin",
    auth_provider=AdminAuthProvider(),
    middlewares=[
        Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=False),
    ],
)

admin.add_view(UserView(User))

__all__ = ["admin"]
