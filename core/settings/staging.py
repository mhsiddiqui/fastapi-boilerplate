from .base import *  # noqa F403


class Settings(
    AppSettings,  # noqa F405
    CryptSettings,  # noqa F405
    DatabaseSettings,  # noqa F405
    RedisCacheSettings,  # noqa F405
    ClientSideCacheSettings,  # noqa F405
    RedisQueueSettings,  # noqa F405
    MediaSettings,  # noqa F405
    EnvironmentSettings,  # noqa F405
    OTPSettings,  # noqa F405
):
    MIDDLEWARES = AppSettings.MIDDLEWARES + [  # noqa F405
        Middleware(  # noqa F405
            "src.app.utils.middlewares.client_cache_middleware.ClientCacheMiddleware",
            kwargs={"max_age": ClientSideCacheSettings.CLIENT_CACHE_MAX_AGE},  # noqa F405
        )
    ]
