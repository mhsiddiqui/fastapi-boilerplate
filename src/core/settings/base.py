from enum import Enum
from pathlib import Path
from pydoc import locate

from pydantic import computed_field
from pydantic_settings import BaseSettings
from starlette.config import Config

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent.parent
env_path = str(BASE_DIR / ".env")
config = Config(env_path)


class Middleware:
    def __init__(self, middleware_class, args=None, kwargs=None):
        self.middleware_class = locate(middleware_class)
        self.args = args or []
        self.kwargs = kwargs or {}


def _parse_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class AppSettings(BaseSettings):
    BASE_DIR: Path = BASE_DIR
    SERVER_URL: str = config("SERVER_URL", default="http://localhost:8000")
    TEMPLATE_PATH: str = str(BASE_DIR / "src")
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)
    MIDDLEWARES: list[Middleware] = []
    TEMPLATES_DIR: str = str(BASE_DIR / "src" / "templates")
    INSTALLED_APPS: list[str] = []
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    CORS_ALLOW_ORIGINS: list[str] = _parse_csv(config("CORS_ALLOW_ORIGINS", default=None), ["*"])
    CORS_ALLOW_CREDENTIALS: bool = config("CORS_ALLOW_CREDENTIALS", cast=bool, default=True)
    CORS_ALLOW_METHODS: list[str] = _parse_csv(config("CORS_ALLOW_METHODS", default=None), ["*"])
    CORS_ALLOW_HEADERS: list[str] = _parse_csv(config("CORS_ALLOW_HEADERS", default=None), ["*"])


class MediaSettings(BaseSettings):
    MEDIA_URL: str | None = config("MEDIA_ROOT", default="/media")
    MEDIA_ROOT: str | None = config("MEDIA_ROOT", default="medias")
    MEDIA_STORAGE: str = config("MEDIA_STORAGE", default="fastapi_storages.FileSystemStorage")


class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", cast=int, default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    POSTGRES_URL: str | None = config("POSTGRES_URL", default=None)
    POSTGRES_ECHO: bool = config("POSTGRES_ECHO", cast=bool, default=False)
    POSTGRES_POOL_PRE_PING: bool = config("POSTGRES_POOL_PRE_PING", cast=bool, default=True)

    @computed_field
    @property
    def POSTGRES_URI(self) -> str:
        return f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.POSTGRES_URL:
            return self.POSTGRES_URL
        return f"{self.POSTGRES_ASYNC_PREFIX}{self.POSTGRES_URI}"

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"{self.POSTGRES_SYNC_PREFIX}{self.POSTGRES_URI}"


class RedisCacheSettings(BaseSettings):
    REDIS_CACHE_HOST: str = config("REDIS_CACHE_HOST", default="localhost")
    REDIS_CACHE_PORT: int = config("REDIS_CACHE_PORT", default=6379)
    REDIS_CACHE_URL: str = f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}"


class ClientSideCacheSettings(BaseSettings):
    CLIENT_CACHE_MAX_AGE: int = config("CLIENT_CACHE_MAX_AGE", default=60)


class RedisQueueSettings(BaseSettings):
    REDIS_QUEUE_HOST: str = config("REDIS_QUEUE_HOST", default="localhost")
    REDIS_QUEUE_PORT: int = config("REDIS_QUEUE_PORT", default=6379)


class EnvironmentOption(Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")
