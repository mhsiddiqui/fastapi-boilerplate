from pydoc import locate
from typing import Any

from fastapi_storages import S3Storage

from .settings import settings


class PublicAssetS3Storage(S3Storage):
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_S3_BUCKET_NAME = settings.AWS_S3_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = settings.AWS_S3_ENDPOINT_URL
    AWS_DEFAULT_ACL = settings.AWS_DEFAULT_ACL
    AWS_S3_USE_SSL = settings.AWS_S3_USE_SSL


def get_storage_class(path) -> Any:
    storage_class = locate(settings.MEDIA_STORAGE)
    return storage_class(path=f"{settings.MEDIA_ROOT}/{path}")
