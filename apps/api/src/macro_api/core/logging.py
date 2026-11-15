"""Logging configuration."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from macro_api.config import get_settings


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for attr in ("request_id", "user_id", "method", "path", "status", "latency_ms"):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class _DevFormatter(logging.Formatter):
    """Human-readable for local dev — colour-free to keep Windows terminals sane."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(UTC).strftime("%H:%M:%S")
        base = f"{ts} {record.levelname:<7} {record.name:<28} {record.getMessage()}"
        extras = {
            k: getattr(record, k, None)
            for k in ("request_id", "user_id", "status", "latency_ms")
        }
        extra_str = " ".join(f"{k}={v}" for k, v in extras.items() if v is not None)
        if extra_str:
            base = f"{base}  {extra_str}"
        if record.exc_info:
            base = f"{base}\n{self.formatException(record.exc_info)}"
        return base


def configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    if settings.env == "production":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(_DevFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level)

    # Quiet noisy libraries in development.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)