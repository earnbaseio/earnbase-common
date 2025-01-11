"""Metrics module."""

import logging
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram, Summary
from prometheus_client.registry import CollectorRegistry

logger = logging.getLogger(__name__)


class Metrics:
    """Metrics collection."""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics."""
        self.registry = registry or CollectorRegistry()

        # Initialize request metrics
        self.request_count = Counter(
            "http_requests",
            "Total number of HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.request_in_progress = Gauge(
            "http_requests_in_progress",
            "Number of HTTP requests in progress",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.request_latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.request_size = Summary(
            "http_request_size_bytes",
            "HTTP request size in bytes",
            ["method", "endpoint"],
            registry=self.registry,
        )

        self.response_size = Summary(
            "http_response_size_bytes",
            "HTTP response size in bytes",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        # Database metrics
        self.db_operation_count = Counter(
            "db_operations_total",
            "Total number of database operations",
            ["operation", "collection"],
            registry=self.registry,
        )

        self.db_operation_latency = Histogram(
            "db_operation_duration_seconds",
            "Database operation duration in seconds",
            ["operation", "collection"],
            registry=self.registry,
        )

        self.db_connections = Gauge(
            "db_connections",
            "Number of active database connections",
            registry=self.registry,
        )

        # Service metrics
        self.service_info = Gauge(
            "service_info",
            "Service information",
            ["version", "environment"],
            registry=self.registry,
        )

        self.service_uptime = Gauge(
            "service_uptime_seconds",
            "Service uptime in seconds",
            registry=self.registry,
        )

        logger.info("Metrics initialized")

    def track_request(
        self,
        method: str,
        endpoint: str,
        status: str,
        request_size: float,
        response_size: float,
        duration: float,
    ) -> None:
        """Track HTTP request metrics."""
        labels = {"method": method, "endpoint": endpoint}
        status_labels = {**labels, "status": status}

        self.request_count.labels(**status_labels).inc()
        self.request_latency.labels(**labels).observe(duration)
        self.request_size.labels(**labels).observe(request_size)
        self.response_size.labels(**status_labels).observe(response_size)

    def start_request(self, method: str, endpoint: str) -> None:
        """Track start of HTTP request."""
        self.request_in_progress.labels(method=method, endpoint=endpoint).inc()

    def end_request(self, method: str, endpoint: str) -> None:
        """Track end of HTTP request."""
        self.request_in_progress.labels(method=method, endpoint=endpoint).dec()


# Create global metrics instance
metrics = Metrics()
