"""
Logging configuration for the application.

Supports structured JSON logging for production and human-readable console
logging for development. In development, also writes JSON logs to a file.

Production logs include:
- ISO 8601 timestamps with timezone
- Service name and version
- Environment identifier
- Trace/request IDs for correlation
- File, line, and function for debugging
"""

import contextvars
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from app.config.settings import get_settings

# Context variables for request-scoped data
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
trace_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_id", default=None
)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)


def set_request_context(
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """Set request-scoped context for logging."""
    if request_id:
        request_id_ctx.set(request_id)
    if trace_id:
        trace_id_ctx.set(trace_id)
    if user_id:
        user_id_ctx.set(user_id)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())[:8]


class ProductionJsonFormatter(jsonlogger.JsonFormatter):
    """Production-ready JSON formatter with comprehensive fields."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("json_indent", 2)
        super().__init__(*args, **kwargs)
        self.settings = get_settings()

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # ISO 8601 timestamp with timezone
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # Service identification
        log_record["service"] = self.settings.app_name
        log_record["version"] = self.settings.app_version
        log_record["environment"] = self.settings.environment.value

        # Request context (if available)
        if request_id_ctx.get():
            log_record["request_id"] = request_id_ctx.get()
        if trace_id_ctx.get():
            log_record["trace_id"] = trace_id_ctx.get()
        if user_id_ctx.get():
            log_record["user_id"] = user_id_ctx.get()

        # Code location
        log_record["file"] = record.filename
        log_record["line"] = record.lineno
        log_record["function"] = record.funcName

        # Exception info
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging(
    log_level: Optional[str] = None,
    json_format: Optional[bool] = None,
) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, uses settings.
        json_format: Whether to use JSON format. If None, uses settings.
    """
    settings = get_settings()

    # Use provided values or fall back to settings
    level = log_level or settings.log_level
    use_json = json_format if json_format is not None else settings.log_json_format

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Set formatter based on configuration
    if use_json:
        console_formatter = ProductionJsonFormatter()
    else:
        console_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # In development, also write JSON logs to a file
    if not use_json:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(level)
        file_formatter = ProductionJsonFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={level}, json_format={use_json}, "
        f"environment={settings.environment.value}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name, typically __name__ of the module.

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
