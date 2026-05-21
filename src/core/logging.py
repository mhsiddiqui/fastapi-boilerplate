"""Logging configuration.

Called once from ``src/core/setup.py`` before the FastAPI app is built so
uvicorn workers and application code share the same handler/formatter.
Override the level via the ``LOG_LEVEL`` env var.
"""

import logging
import logging.config
from typing import Any


def configure_logging(level: str = "INFO") -> None:
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {"level": level, "handlers": ["default"]},
        "loggers": {
            # uvicorn ships its own loggers; route them through ours.
            "uvicorn.error": {"level": level, "handlers": ["default"], "propagate": False},
            "uvicorn.access": {"level": level, "handlers": ["default"], "propagate": False},
            # SQLAlchemy is chatty at INFO; keep it quiet unless explicitly enabled.
            "sqlalchemy.engine": {"level": "WARNING", "handlers": ["default"], "propagate": False},
        },
    }
    logging.config.dictConfig(config)
