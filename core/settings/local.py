from .base import *  # noqa F403


class Settings(
    AppSettings,  # noqa F405
    CryptSettings,  # noqa F405
    DatabaseSettings,  # noqa F405
    # RedisCacheSettings,
    # ClientSideCacheSettings,
    # RedisQueueSettings,
    MediaSettings,  # noqa F405
    EnvironmentSettings,  # noqa F405
):
    pass
