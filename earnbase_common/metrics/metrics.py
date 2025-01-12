"""Metrics collection."""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import Counter as PrometheusCounter
from prometheus_client import Gauge as PrometheusGauge
from prometheus_client import Histogram as PrometheusHistogram
from prometheus_client import Summary as PrometheusSummary
from prometheus_client import generate_latest


class MetricsManager:
    """Metrics manager for standardized metrics collection."""

    DEFAULT_BUCKETS = (
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    )

    def __init__(self, namespace: str = "earnbase"):
        """Initialize metrics manager."""
        self.namespace = namespace
        self._counters: Dict[str, PrometheusCounter] = {}
        self._histograms: Dict[str, PrometheusHistogram] = {}
        self._gauges: Dict[str, PrometheusGauge] = {}
        self._summaries: Dict[str, PrometheusSummary] = {}

    def _format_name(self, name: str) -> str:
        """Format metric name."""
        return f"{self.namespace}_{name}"

    def counter(
        self, name: str, labelnames: Optional[List[str]] = None
    ) -> PrometheusCounter:
        """Get or create counter metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._counters:
            self._counters[metric_name] = PrometheusCounter(
                metric_name,
                name,
                labelnames=labelnames or [],
            )
        return self._counters[metric_name]

    def histogram(
        self,
        name: str,
        label_names: List[str],
        buckets: Optional[tuple] = None,
    ) -> PrometheusHistogram:
        """Get or create histogram metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._histograms:
            self._histograms[metric_name] = PrometheusHistogram(
                metric_name,
                name,
                label_names,
                buckets=buckets or self.DEFAULT_BUCKETS,
            )
        return self._histograms[metric_name]

    def gauge(
        self, name: str, labelnames: Optional[List[str]] = None
    ) -> PrometheusGauge:
        """Get or create gauge metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._gauges:
            self._gauges[metric_name] = PrometheusGauge(
                metric_name,
                metric_name,
                labelnames=labelnames or [],
            )
        return self._gauges[metric_name]

    def summary(
        self, name: str, labelnames: Optional[List[str]] = None
    ) -> PrometheusSummary:
        """Get or create summary metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._summaries:
            self._summaries[metric_name] = PrometheusSummary(
                metric_name,
                metric_name,
                labelnames=labelnames or [],
            )
        return self._summaries[metric_name]


class MetricsDecorator:
    """Decorator for metrics collection."""

    def __init__(self, metrics_manager: MetricsManager):
        """Initialize metrics decorator."""
        self.metrics = metrics_manager

    def counter(self, name: str, labelnames: Optional[List[str]] = None) -> Callable:
        """Counter decorator."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                metric = self.metrics.counter(name, labelnames)
                try:
                    result = func(*args, **kwargs)
                    metric.inc()
                    return result
                except Exception as e:
                    metric.labels(status="error").inc()
                    raise e

            return wrapper

        return decorator

    def histogram(
        self,
        name: str,
        label_names: List[str],
        buckets: Optional[tuple] = None,
    ) -> Callable:
        """Histogram decorator."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                metric = self.metrics.histogram(name, label_names, buckets)
                with metric.time():
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        raise e

            return wrapper

        return decorator


# Create single instance of MetricsManager
metrics = MetricsManager()

# Database metrics
db_operation_latency = metrics.histogram(
    "db_operation_duration_seconds",
    ["operation", "collection"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)
db_operation_count = metrics.counter(
    "db_operations_total",
    labelnames=["operation", "collection"],
)

# HTTP metrics
http_request_latency = metrics.histogram(
    "http_request_duration_seconds",
    ["method", "path", "status"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)
http_request_count = metrics.counter(
    "http_requests_total",
    labelnames=["method", "path", "status"],
)
http_request_in_progress = metrics.gauge(
    "http_requests_in_progress",
    labelnames=["method", "path"],
)
http_request_size = metrics.summary(
    "http_request_size_bytes",
    labelnames=["method", "path"],
)
http_response_size = metrics.summary(
    "http_response_size_bytes",
    labelnames=["method", "path"],
)

# Service metrics
service_info = metrics.gauge(
    "service_info",
    labelnames=["version", "environment"],
)
service_uptime = metrics.gauge(
    "service_uptime_seconds",
    None,
)

# Export public interface
__all__ = [
    "metrics",
    "db_operation_latency",
    "db_operation_count",
    "http_request_latency",
    "http_request_count",
    "http_request_in_progress",
    "http_request_size",
    "http_response_size",
    "service_info",
    "service_uptime",
    "CONTENT_TYPE_LATEST",
    "generate_latest",
]
