"""Process-local rate limiter used to protect auth endpoints.

The default ``slowapi`` storage is in-memory — fine for single-process dev,
but you'll want redis storage in production. Swap by setting
``storage_uri="redis://..."``.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
