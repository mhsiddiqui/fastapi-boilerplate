from .base import *  # noqa F403


class Settings(
    AppSettings,  # noqa F405
    CryptSettings,  # noqa F405
    DatabaseSettings,  # noqa F405
    # RedisCacheSettings,   F405
    # ClientSideCacheSettings,   F405
    # RedisQueueSettings,   F405
    MediaSettings,  # noqa F405
    EnvironmentSettings,  # noqa F405
    OTPSettings,  # noqa F405
    AWSSettings,  # noqa F405
):
    pass


settings = Settings()
