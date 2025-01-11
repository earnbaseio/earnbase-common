"""Tests for metrics manager."""

import pytest
from earnbase_common.metrics import MetricsManager
from prometheus_client import Counter, Gauge, Histogram, Summary


@pytest.mark.unit
@pytest.mark.metrics
class TestMetricsManager:
    """Test metrics manager."""

    @pytest.fixture
    def metrics_manager(self):
        """Create metrics manager instance."""
        return MetricsManager(namespace="test")

    def test_format_name(self, metrics_manager):
        """Test metric name formatting."""
        assert metrics_manager._format_name("test_metric") == "test_test_metric"

    def test_counter_creation(self, metrics_manager):
        """Test counter metric creation."""
        # Create counter without labels
        counter = metrics_manager.counter("requests_total")
        assert isinstance(counter, Counter)
        assert counter._name == "test_requests_total"

        # Create counter with labels
        counter = metrics_manager.counter(
            "requests_total",
            labels={"method": "GET", "endpoint": "/test"},
        )
        assert isinstance(counter, Counter)
        assert counter._name == "test_requests_total"
        assert "method" in counter._labelnames
        assert "endpoint" in counter._labelnames

        # Get existing counter
        counter2 = metrics_manager.counter(
            "requests_total",
            labels={"method": "GET", "endpoint": "/test"},
        )
        assert counter is counter2

    def test_histogram_creation(self, metrics_manager):
        """Test histogram metric creation."""
        # Create histogram with default buckets
        histogram = metrics_manager.histogram(
            "request_duration",
            label_names=["method", "endpoint"],
        )
        assert isinstance(histogram, Histogram)
        assert histogram._name == "test_request_duration"
        assert "method" in histogram._labelnames
        assert "endpoint" in histogram._labelnames

        # Create histogram with custom buckets
        custom_buckets = (0.1, 0.5, 1.0, 5.0)
        histogram = metrics_manager.histogram(
            "request_duration_custom",
            label_names=["method"],
            buckets=custom_buckets,
        )
        assert isinstance(histogram, Histogram)
        assert histogram._name == "test_request_duration_custom"
        assert histogram._buckets == custom_buckets

        # Get existing histogram
        histogram2 = metrics_manager.histogram(
            "request_duration_custom",
            label_names=["method"],
        )
        assert histogram is histogram2

    def test_gauge_creation(self, metrics_manager):
        """Test gauge metric creation."""
        # Create gauge without labels
        gauge = metrics_manager.gauge("active_connections")
        assert isinstance(gauge, Gauge)
        assert gauge._name == "test_active_connections"

        # Create gauge with labels
        gauge = metrics_manager.gauge(
            "active_connections",
            labels={"pool": "main"},
        )
        assert isinstance(gauge, Gauge)
        assert gauge._name == "test_active_connections"
        assert "pool" in gauge._labelnames

        # Get existing gauge
        gauge2 = metrics_manager.gauge(
            "active_connections",
            labels={"pool": "main"},
        )
        assert gauge is gauge2

    def test_summary_creation(self, metrics_manager):
        """Test summary metric creation."""
        # Create summary without labels
        summary = metrics_manager.summary("response_size")
        assert isinstance(summary, Summary)
        assert summary._name == "test_response_size"

        # Create summary with labels
        summary = metrics_manager.summary(
            "response_size",
            labels={"content_type": "json"},
        )
        assert isinstance(summary, Summary)
        assert summary._name == "test_response_size"
        assert "content_type" in summary._labelnames

        # Get existing summary
        summary2 = metrics_manager.summary(
            "response_size",
            labels={"content_type": "json"},
        )
        assert summary is summary2

    def test_metrics_namespace(self):
        """Test metrics namespace."""
        # Test default namespace
        manager = MetricsManager()
        assert manager.namespace == "earnbase"
        assert manager._format_name("test") == "earnbase_test"

        # Test custom namespace
        manager = MetricsManager(namespace="custom")
        assert manager.namespace == "custom"
        assert manager._format_name("test") == "custom_test"
