"""Dramatiq broker setup and actor registry.

Importing this package wires up the Redis broker; importing it again is a
no-op. Both the web process (when enqueueing tasks) and the worker
(``dramatiq src.tasks``) load this module, so the broker is configured once
in either context.
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from src.core.settings import settings

_broker = RedisBroker(
    host=settings.REDIS_QUEUE_HOST,
    port=settings.REDIS_QUEUE_PORT,
)
dramatiq.set_broker(_broker)

# Import all actor modules so ``dramatiq src.tasks`` discovers them.
from src.tasks.emails import send_welcome_email  # noqa: E402, F401

__all__ = ["send_welcome_email"]
