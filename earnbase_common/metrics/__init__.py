"""Common metrics module."""

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from earnbase_common.metrics.metrics import Metrics, metrics

__all__ = ["Metrics", "metrics", "generate_latest", "CONTENT_TYPE_LATEST"]
