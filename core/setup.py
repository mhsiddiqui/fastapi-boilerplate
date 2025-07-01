from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import fastapi
from fastapi import APIRouter, Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware

from core.db.database import Base
from core.db.database import async_engine as engine
from src.utils.authentication import get_current_superuser
from src.utils.exceptions.handlers import setup_exception_handlers

from .admin import admin
from .easy_router.initializer import AppsInitializer, RoutesInitializer
from .settings import setting_class, settings
from .settings.base import (
    AppSettings,
    DatabaseSettings,
    EnvironmentOption,
    EnvironmentSettings,
)

configs = BabelConfigs(
    ROOT_DIR=str(settings.BASE_DIR),
    BABEL_DOMAIN=str(settings.BASE_DIR / "locale" / "messages.pot"),
    BABEL_CONFIG_FILE=str(settings.BASE_DIR / "babel.cfg"),
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="locale",
)
babel = Babel(configs=configs)


# -------------- database --------------
async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def lifespan_factory(
    app_settings: setting_class,
    create_tables_on_start: bool = True,
) -> Any:
    """Factory to create a lifespan async context manager for a FastAPI app."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        if isinstance(app_settings, DatabaseSettings) and create_tables_on_start:
            await create_tables()

        yield

    return lifespan


class ApplicationFactory:
    """
    Creates and configures a FastAPI application based on the provided settings.

    This function initializes a FastAPI application and configures it with various settings
    and handlers based on the type of the `settings` object provided.

    Parameters
    ----------
    router : APIRouter
        The APIRouter object containing the routes to be included in the FastAPI application.

    settings
        An instance representing the settings for configuring the FastAPI application.
        It determines the configuration applied:

        - AppSettings: Configures basic app metadata like name, description, contact, and license info.
        - DatabaseSettings: Adds event handlers for initializing database tables during startup.
        - RedisCacheSettings: Sets up event handlers for creating and closing a Redis cache pool.
        - ClientSideCacheSettings: Integrates middleware for client-side caching.
        - RedisQueueSettings: Sets up event handlers for creating and closing a Redis queue pool.
        - RedisRateLimiterSettings: Sets up event handlers for creating and closing a Redis rate limiter pool.
        - EnvironmentSettings: Conditionally sets documentation URLs and integrates custom routes for API documentation
          based on the environment type.

    create_tables_on_start : bool
        A flag to indicate whether to create database tables on application startup.
        Defaults to True.

    **kwargs
        Additional keyword arguments passed directly to the FastAPI constructor.

    Returns
    -------

    The function configures the FastAPI application with different features and behaviors
    based on the provided settings. It includes setting up database connections, Redis pools
    for caching, queue, and rate limiting, client-side caching, and customizing the API documentation
    based on the environment settings.
    """

    def __init__(
        self,
        create_tables_on_start: bool = True,
        **kwargs: Any,
    ) -> None:
        # self.router = router
        self.settings = settings
        self.create_tables_on_start = create_tables_on_start
        self.data = kwargs

    def setup_data(self):
        if isinstance(self.settings, AppSettings):
            to_update = {
                "title": self.settings.APP_NAME,
                "description": self.settings.APP_DESCRIPTION,
                "contact": {"name": self.settings.CONTACT_NAME, "email": self.settings.CONTACT_EMAIL},
                "license_info": {"name": self.settings.LICENSE_NAME},
            }
            self.data.update(to_update)

        if isinstance(self.settings, EnvironmentSettings):
            self.data.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    def initialize_application(self):
        lifespan = lifespan_factory(self.settings, create_tables_on_start=self.create_tables_on_start)
        application = FastAPI(lifespan=lifespan, **self.data)
        return application

    def initialize_admin(self, application):
        admin.mount_to(application)

    def add_middlewares(self, application):
        for middleware in self.settings.MIDDLEWARES:
            application.add_middleware(middleware.middleware_class, *middleware.args, **middleware.kwargs)

    def setup_docs(self, application):
        if isinstance(self.settings, EnvironmentSettings):
            if self.settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
                docs_router = APIRouter()
                if self.settings.ENVIRONMENT != EnvironmentOption.LOCAL:
                    docs_router = APIRouter(dependencies=[Depends(get_current_superuser)])

                @docs_router.get("/docs", include_in_schema=False)
                async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
                    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

                @docs_router.get("/redoc", include_in_schema=False)
                async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
                    return get_redoc_html(openapi_url="/openapi.json", title="docs")

                @docs_router.get("/openapi.json", include_in_schema=False)
                async def openapi() -> dict[str, Any]:
                    out: dict = get_openapi(
                        title=application.title, version=application.version, routes=application.routes
                    )
                    return out

                application.include_router(docs_router)

    def initialize_routes(self, application):
        RoutesInitializer(app=application, package="core.routes").initialize()

    def add_babel_settings(self, application):
        application.add_middleware(BabelMiddleware, babel_configs=configs)

    def initialize_apps(self, application):
        AppsInitializer(app=application, package="src", installed_apps=INSTALLED_APPS).initialize()

    def init(self):
        self.setup_data()
        application = self.initialize_application()
        setup_exception_handlers(application)
        self.initialize_admin(application)
        self.initialize_routes(application)
        self.initialize_apps(application)
        self.add_middlewares(application)
        self.setup_docs(application)
        return application
