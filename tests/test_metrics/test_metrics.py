"""Tests for metrics collector."""

from unittest.mock import patch

import pytest
from earnbase_common.metrics.metrics import Metrics
from prometheus_client import Counter, Gauge, Histogram


@pytest.mark.unit
@pytest.mark.metrics
class TestMetrics:
    """Test metrics collector."""

    def test_metrics_initialization(self):
        """Test metrics initialization."""
        with patch("earnbase_common.metrics.metrics.logger") as mock_logger:
            metrics = Metrics()

            # Test HTTP request metrics
            assert isinstance(metrics.request_count, Counter)
            assert metrics.request_count._name == "http_requests_total"
            assert set(metrics.request_count._labelnames) == {
                "method",
                "endpoint",
                "status",
            }

            assert isinstance(metrics.request_latency, Histogram)
            assert metrics.request_latency._name == "http_request_duration_seconds"
            assert set(metrics.request_latency._labelnames) == {"method", "endpoint"}

            assert isinstance(metrics.request_in_progress, Gauge)
            assert metrics.request_in_progress._name == "http_requests_in_progress"
            assert set(metrics.request_in_progress._labelnames) == {
                "method",
                "endpoint",
            }

            # Test database metrics
            assert isinstance(metrics.db_operation_count, Counter)
            assert metrics.db_operation_count._name == "db_operations_total"
            assert set(metrics.db_operation_count._labelnames) == {
                "operation",
                "collection",
            }

            assert isinstance(metrics.db_operation_latency, Histogram)
            assert metrics.db_operation_latency._name == "db_operation_duration_seconds"
            assert set(metrics.db_operation_latency._labelnames) == {
                "operation",
                "collection",
            }

            assert isinstance(metrics.db_connections, Gauge)
            assert metrics.db_connections._name == "db_connections"
            assert not metrics.db_connections._labelnames

            # Test service metrics
            assert isinstance(metrics.service_info, Gauge)
            assert metrics.service_info._name == "service_info"
            assert set(metrics.service_info._labelnames) == {"version", "environment"}

            assert isinstance(metrics.service_uptime, Gauge)
            assert metrics.service_uptime._name == "service_uptime_seconds"
            assert not metrics.service_uptime._labelnames

            # Verify logging
            mock_logger.info.assert_called_once_with("Metrics initialized")

    def test_metrics_usage(self):
        """Test metrics usage."""
        metrics = Metrics()

        # Test HTTP request metrics
        metrics.request_count.labels(method="GET", endpoint="/test", status="200").inc()
        with metrics.request_latency.labels(method="GET", endpoint="/test").time():
            pass
        metrics.request_in_progress.labels(method="GET", endpoint="/test").inc()
        metrics.request_in_progress.labels(method="GET", endpoint="/test").dec()

        # Test database metrics
        metrics.db_operation_count.labels(operation="find", collection="users").inc()
        with metrics.db_operation_latency.labels(
            operation="find", collection="users"
        ).time():
            pass
        metrics.db_connections.set(5)

        # Test service metrics
        metrics.service_info.labels(version="1.0.0", environment="test").set(1)
        metrics.service_uptime.set(3600)

    def test_global_metrics_instance(self):
        """Test global metrics instance."""
        from earnbase_common.metrics.metrics import metrics

        assert isinstance(metrics, Metrics)
        assert metrics.request_count._name == "http_requests_total"
