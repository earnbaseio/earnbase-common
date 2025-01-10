"""Logging configuration module."""

import logging
import logging.config
import logging.handlers
import os
import sys
from typing import Any, Dict

import structlog
from earnbase_common.logging.processors import add_service_info, filter_sensitive_data
from structlog.dev import ConsoleRenderer
from structlog.stdlib import ProcessorFormatter


def ensure_log_dir(log_file: str) -> None:
    """Ensure log directory exists."""
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)


def get_shared_processors() -> list:
    """Get shared processors for all formatters."""
    return [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_service_info,
        filter_sensitive_data,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def get_logging_config(
    service_name: str,
    log_file: str,
    log_level: str = "INFO",
    debug: bool = False,
) -> Dict[str, Any]:
    """Get logging configuration dictionary."""
    # Ensure log directory exists
    ensure_log_dir(log_file)

    error_log = os.path.join(os.path.dirname(log_file), f"{service_name}-error.log")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": get_shared_processors(),
            },
            "colored": {
                "()": ProcessorFormatter,
                "processor": ConsoleRenderer(
                    colors=True,
                    exception_formatter=structlog.dev.plain_traceback,
                ),
                "foreign_pre_chain": get_shared_processors(),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored" if debug else "json",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": error_log,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "ERROR",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file", "error_file"],
                "level": log_level,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
            },
            "uvicorn.error": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def setup_logging(
    service_name: str,
    log_file: str,
    log_level: str = "INFO",
    debug: bool = False,
) -> None:
    """Set up structured logging."""
    # Configure structlog
    structlog.configure(
        processors=get_shared_processors()
        + [
            (
                structlog.processors.JSONRenderer()
                if not debug
                else structlog.dev.ConsoleRenderer(colors=True)
            )
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.config.dictConfig(
        get_logging_config(
            service_name=service_name,
            log_file=log_file,
            log_level=log_level,
            debug=debug,
        )
    )
