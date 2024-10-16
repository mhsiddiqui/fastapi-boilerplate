from .base import *


class Settings(
    AppSettings,
    CryptSettings,
    DatabaseSettings,
    RedisCacheSettings,
    ClientSideCacheSettings,
    RedisQueueSettings,
    MediaSettings,
    EnvironmentSettings
):
    MIDDLEWARES = [
        Middleware('src.app.utils.middlewares.client_cache_middleware.ClientCacheMiddleware', kwargs={
            'max_age': ClientSideCacheSettings.CLIENT_CACHE_MAX_AGE
        })
    ]
