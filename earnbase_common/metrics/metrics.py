"""Metrics module."""

from earnbase_common.logging import get_logger
from prometheus_client import Counter, Gauge, Histogram

logger = get_logger(__name__)


class Metrics:
    """Metrics collector."""

    def __init__(self):
        """Initialize metrics."""
        # Request metrics
        self.request_count = Counter(
            "http_requests_total",
            "Total number of HTTP requests",
            ["method", "endpoint", "status"],
        )
        self.request_latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
        )
        self.request_in_progress = Gauge(
            "http_requests_in_progress",
            "Number of HTTP requests in progress",
            ["method", "endpoint"],
        )

        # Database metrics
        self.db_operation_count = Counter(
            "db_operations_total",
            "Total number of database operations",
            ["operation", "collection"],
        )
        self.db_operation_latency = Histogram(
            "db_operation_duration_seconds",
            "Database operation duration in seconds",
            ["operation", "collection"],
        )
        self.db_connections = Gauge(
            "db_connections",
            "Number of active database connections",
        )

        # Service metrics
        self.service_info = Gauge(
            "service_info",
            "Service information",
            ["version", "environment"],
        )
        self.service_uptime = Gauge(
            "service_uptime_seconds",
            "Service uptime in seconds",
        )

        logger.info("metrics_initialized")


# Global metrics instance
metrics = Metrics()
