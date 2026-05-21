from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.core.db.database import Base
from src.core.db.database import async_engine as engine
from src.core.exceptions.handlers import setup_exception_handlers
from src.core.logging import configure_logging
from src.core.rate_limit import limiter
from src.core.settings import setting_class, settings
from src.core.settings.base import (
    AppSettings,
    DatabaseSettings,
    EnvironmentOption,
    EnvironmentSettings,
)


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


def _is_production(app_settings: Any) -> bool:
    return (
        isinstance(app_settings, EnvironmentSettings)
        and app_settings.ENVIRONMENT == EnvironmentOption.PRODUCTION
    )


class ApplicationFactory:
    """Creates and configures a FastAPI application based on the provided settings."""

    def __init__(
        self,
        create_tables_on_start: bool = True,
        **kwargs: Any,
    ) -> None:
        self.settings = settings
        self.create_tables_on_start = create_tables_on_start
        self.data = kwargs

    def setup_data(self) -> None:
        if isinstance(self.settings, AppSettings):
            self.data.update(
                {
                    "title": self.settings.APP_NAME,
                    "description": self.settings.APP_DESCRIPTION,
                    "contact": {"name": self.settings.CONTACT_NAME, "email": self.settings.CONTACT_EMAIL},
                    "license_info": {"name": self.settings.LICENSE_NAME},
                }
            )
        # Hide OpenAPI surface in production unless explicitly overridden.
        if _is_production(self.settings):
            self.data.setdefault("docs_url", None)
            self.data.setdefault("redoc_url", None)
            self.data.setdefault("openapi_url", None)

    def initialize_application(self) -> FastAPI:
        lifespan = lifespan_factory(self.settings, create_tables_on_start=self.create_tables_on_start)
        return FastAPI(lifespan=lifespan, **self.data)

    def add_middlewares(self, application: FastAPI) -> None:
        if isinstance(self.settings, AppSettings):
            application.add_middleware(
                CORSMiddleware,
                allow_origins=self.settings.CORS_ALLOW_ORIGINS,
                allow_credentials=self.settings.CORS_ALLOW_CREDENTIALS,
                allow_methods=self.settings.CORS_ALLOW_METHODS,
                allow_headers=self.settings.CORS_ALLOW_HEADERS,
            )
        for middleware in self.settings.MIDDLEWARES:
            application.add_middleware(middleware.middleware_class, *middleware.args, **middleware.kwargs)

    def init(self) -> FastAPI:
        self.setup_data()
        application = self.initialize_application()
        setup_exception_handlers(application)
        self.add_middlewares(application)
        # Rate limiting (slowapi) — handler + middleware + state for @limiter.limit(...)
        application.state.limiter = limiter
        application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        application.add_middleware(SlowAPIMiddleware)
        return application


# Configure logging once, at import time, so uvicorn workers inherit it.
configure_logging(getattr(settings, "LOG_LEVEL", "INFO"))


# ----- app instance (uvicorn target: ``src.core.setup:app``) -----
# Tables are managed by Alembic — disable the lifespan create_all path.
from src.admin import admin  # noqa: E402
from src.app import api_router, root_router  # noqa: E402

app = ApplicationFactory(create_tables_on_start=False).init()
app.include_router(api_router)
app.include_router(root_router)
admin.mount_to(app)
