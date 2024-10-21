from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin

from core.db.database import async_engine as engine
from src.utils.authentication import UsernameAndPasswordProvider

from .settings import settings

admin = Admin(
    engine,
    title=settings.APP_NAME,
    auth_provider=UsernameAndPasswordProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)],
)
