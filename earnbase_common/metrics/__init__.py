"""Metrics utilities."""

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
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> PrometheusCounter:
        """Get or create counter metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._counters:
            self._counters[metric_name] = PrometheusCounter(
                metric_name,
                name,
                list(labels.keys()) if labels else [],
            )
        counter = self._counters[metric_name]
        if labels:
            counter = counter.labels(**labels)
        return counter

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
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> PrometheusGauge:
        """Get or create gauge metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._gauges:
            label_names = list(labels.keys()) if labels else []
            self._gauges[metric_name] = PrometheusGauge(
                metric_name,
                metric_name,
                labelnames=label_names,
            )
        gauge = self._gauges[metric_name]
        if labels:
            return gauge.labels(**labels)
        return gauge

    def summary(
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> PrometheusSummary:
        """Get or create summary metric."""
        metric_name = self._format_name(name)
        if metric_name not in self._summaries:
            label_names = list(labels.keys()) if labels else []
            self._summaries[metric_name] = PrometheusSummary(
                metric_name,
                metric_name,
                labelnames=label_names,
            )
        summary = self._summaries[metric_name]
        if labels:
            return summary.labels(**labels)
        return summary


class MetricsDecorator:
    """Decorator for metrics collection."""

    def __init__(self, metrics_manager: MetricsManager):
        """Initialize metrics decorator."""
        self.metrics = metrics_manager

    def counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> Callable:
        """Counter decorator."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                metric = self.metrics.counter(name, labels)
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
_metrics_manager = MetricsManager()

# Export public interface
counter = _metrics_manager.counter
histogram = _metrics_manager.histogram
gauge = _metrics_manager.gauge
summary = _metrics_manager.summary
metrics_decorator = MetricsDecorator(_metrics_manager)

__all__ = [
    "MetricsManager",
    "MetricsDecorator",
    "counter",
    "histogram",
    "gauge",
    "summary",
    "metrics_decorator",
    "CONTENT_TYPE_LATEST",
    "generate_latest",
]
