from enum import Enum
from pathlib import Path
from pydoc import locate

from pydantic_settings import BaseSettings
from starlette.config import Config

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
env_path = str(BASE_DIR / ".env")
config = Config(env_path)


class Middleware:
    def __init__(self, middleware_class, args=None, kwargs=None):
        self.middleware_class = locate(middleware_class)
        self.args = args or []
        self.kwargs = kwargs or {}


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
    INSTALLED_APPS: list[str] = ["features.auth", "features.account"]


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
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    POSTGRES_URI: str = f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    POSTGRES_URL: str | None = config("POSTGRES_URL", default=None)


class AWSSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY: str = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_S3_BUCKET_NAME: str = config("AWS_S3_BUCKET_NAME", default="bucket-name")
    AWS_S3_ENDPOINT_URL: str = config("AWS_S3_ENDPOINT_URL", default="s3.amazonaws.com")
    AWS_DEFAULT_ACL: str = config("AWS_DEFAULT_ACL", default="public-read")
    AWS_S3_USE_SSL: bool = config("AWS_S3_USE_SSL", default=True)


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


class MailBackend(Enum):
    FILE = "file"
    SMTP = "smtp"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class EmailSettings(BaseSettings):
    MAIL_FILES_PATH: str = str(BASE_DIR / "src" / config("MAIL_FILES_PATH", default="temp-emails/"))
    MAIL_BACKEND: MailBackend = config("MAIL_BACKEND", default="file")
    MAIL_USERNAME: str = config("MAIL_USERNAME", default="user")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD", default="password")
    MAIL_FROM: str = config("MAIL_FROM", default="from")
    MAIL_PORT: int = config("MAIL_PORT", default=587)
    MAIL_SERVER: str = config("MAIL_SERVER", default="smtp.gmail.com")
    MAIL_FROM_NAME: str = config("MAIL_FROM_NAME", default="FastAPI")
    MAIL_STARTTLS: bool = config("MAIL_STARTTLS", default=True)
    MAIL_SSL_TLS: bool = config("MAIL_SSL_TLS", default=False)
    USE_CREDENTIALS: bool = config("USE_CREDENTIALS", default=True)
    VALIDATE_CERTS: bool = config("VALIDATE_CERTS", default=True)


class OTPSettings(BaseSettings):
    OTP_SECRET: str = config("OTP_SECRET", default="base32secret3232")
    OTP_TIMEOUT: int = config("OTP_TIMEOUT", default=5 * 60)
    OTP_DEBUG: bool = config("OTP_DEBUG", default=False)
    TESTING_OTP: int = config("TESTING_OTP", default=123456)
