"""Logging processors module."""

from typing import Any, Dict

import structlog


def add_service_info(
    logger: structlog.BoundLogger, name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add service information to log events."""
    # Service info will be added by the service using this processor
    return event_dict


def filter_sensitive_data(
    logger: structlog.BoundLogger, name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Filter sensitive data from log events."""
    SENSITIVE_KEYS = {
        "password",
        "token",
        "secret",
        "api_key",
        "secret_key",
        "private_key",
        "authorization",
        "access_token",
        "refresh_token",
    }

    def _is_sensitive(key):
        key = key.lower()
        return any(sensitive in key for sensitive in SENSITIVE_KEYS)

    def _filter_value(value):
        if isinstance(value, dict):
            return _filter_dict(value)
        elif isinstance(value, list):
            return _filter_list(value)
        return value

    def _filter_dict(d):
        if not isinstance(d, dict):
            return d
        return {
            k: "***FILTERED***" if _is_sensitive(k) else _filter_value(v)
            for k, v in d.items()
        }

    def _filter_list(lst):
        return [_filter_value(item) for item in lst]

    return _filter_dict(event_dict)
