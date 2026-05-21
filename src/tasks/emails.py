"""Example email-sending task.

Stub body — real implementations should call into ``fastapi-mail`` (in deps)
or another SMTP/transactional provider. Kept actor-shaped so the worker has
something to register.
"""

import logging

import dramatiq

log = logging.getLogger(__name__)


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60_000)
def send_welcome_email(user_id: str, email: str) -> None:
    log.info("send_welcome_email user_id=%s email=%s", user_id, email)
    # TODO: integrate fastapi-mail or another sender here.
