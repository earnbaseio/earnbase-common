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
    """Filter out sensitive data from logs."""
    sensitive_fields = [
        "password",
        "token",
        "secret",
        "key",
        "authorization",
        "access_token",
        "refresh_token",
        "api_key",
        "private_key",
        "client_secret",
    ]

    def _filter_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter dictionary."""
        filtered = {}
        for k, v in d.items():
            if isinstance(v, dict):
                filtered[k] = _filter_dict(v)
            elif isinstance(v, list):
                filtered[k] = [_filter_dict(i) if isinstance(i, dict) else i for i in v]
            elif any(field in k.lower() for field in sensitive_fields):
                filtered[k] = "***FILTERED***"
            else:
                filtered[k] = v
        return filtered

    return _filter_dict(event_dict)
