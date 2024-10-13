from .base import *


class Settings(
    AppSettings,
    CryptSettings,
    DatabaseSettings,
    # RedisCacheSettings,
    # ClientSideCacheSettings,
    # RedisQueueSettings,
    MediaSettings,
    EnvironmentSettings
):
    pass
