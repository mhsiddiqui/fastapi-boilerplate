from pydoc import locate
from typing import Any

from .settings import settings


def get_storage_class(path) -> Any:
    storage_class = locate(settings.MEDIA_STORAGE)
    return storage_class(path=f"{settings.MEDIA_ROOT}/{path}")
