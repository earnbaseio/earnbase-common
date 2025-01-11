"""Tests for metrics decorator."""

from unittest.mock import MagicMock, patch

import pytest
from earnbase_common.metrics import MetricsDecorator, MetricsManager
from prometheus_client import Counter, Histogram


@pytest.mark.unit
@pytest.mark.metrics
class TestMetricsDecorator:
    """Test metrics decorator."""

    @pytest.fixture
    def metrics_manager(self):
        """Create metrics manager instance."""
        return MetricsManager(namespace="test")

    @pytest.fixture
    def metrics_decorator(self, metrics_manager):
        """Create metrics decorator instance."""
        return MetricsDecorator(metrics_manager)

    def test_counter_decorator_success(self, metrics_decorator):
        """Test counter decorator with successful function execution."""

        # Create a test function
        @metrics_decorator.counter("test_counter", labels={"type": "test"})
        def test_function():
            return "success"

        # Mock the counter
        counter_mock = MagicMock(spec=Counter)
        with patch.object(
            metrics_decorator.metrics, "counter", return_value=counter_mock
        ):
            result = test_function()

            assert result == "success"
            counter_mock.inc.assert_called_once()

    def test_counter_decorator_error(self, metrics_decorator):
        """Test counter decorator with function raising an error."""

        # Create a test function that raises an error
        @metrics_decorator.counter("test_counter", labels={"type": "test"})
        def test_function():
            raise ValueError("test error")

        # Mock the counter
        counter_mock = MagicMock(spec=Counter)
        counter_mock.labels.return_value = counter_mock
        with patch.object(
            metrics_decorator.metrics, "counter", return_value=counter_mock
        ):
            with pytest.raises(ValueError) as exc_info:
                test_function()

            assert str(exc_info.value) == "test error"
            counter_mock.labels.assert_called_once_with(status="error")
            counter_mock.inc.assert_called_once()

    def test_histogram_decorator(self, metrics_decorator):
        """Test histogram decorator."""

        # Create a test function
        @metrics_decorator.histogram(
            "test_histogram",
            label_names=["type"],
            buckets=(0.1, 0.5, 1.0),
        )
        def test_function():
            return "success"

        # Mock the histogram
        histogram_mock = MagicMock(spec=Histogram)
        histogram_mock.time.return_value.__enter__ = MagicMock()
        histogram_mock.time.return_value.__exit__ = MagicMock()

        with patch.object(
            metrics_decorator.metrics, "histogram", return_value=histogram_mock
        ):
            result = test_function()

            assert result == "success"
            histogram_mock.time.assert_called_once()
            histogram_mock.time.return_value.__enter__.assert_called_once()
            histogram_mock.time.return_value.__exit__.assert_called_once()

    def test_histogram_decorator_error(self, metrics_decorator):
        """Test histogram decorator with function raising an error."""

        # Create a test function that raises an error
        @metrics_decorator.histogram(
            "test_histogram",
            label_names=["type"],
        )
        def test_function():
            raise ValueError("test error")

        # Mock the histogram
        histogram_mock = MagicMock(spec=Histogram)
        context_manager = MagicMock()
        context_manager.__enter__ = MagicMock()
        context_manager.__exit__ = MagicMock(
            return_value=False
        )  # Don't suppress exceptions
        histogram_mock.time.return_value = context_manager

        with patch.object(
            metrics_decorator.metrics, "histogram", return_value=histogram_mock
        ):
            with pytest.raises(ValueError) as exc_info:
                test_function()

            assert str(exc_info.value) == "test error"
            histogram_mock.time.assert_called_once()
            context_manager.__enter__.assert_called_once()
            context_manager.__exit__.assert_called_once()

    def test_decorator_preserves_function_metadata(self, metrics_decorator):
        """Test that decorators preserve function metadata."""

        @metrics_decorator.counter("test_counter")
        def test_function():
            """Test function docstring."""
            pass

        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring."

    def test_decorator_with_args_and_kwargs(self, metrics_decorator):
        """Test decorators with function arguments."""

        @metrics_decorator.counter("test_counter")
        def test_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        # Mock the counter
        counter_mock = MagicMock(spec=Counter)
        with patch.object(
            metrics_decorator.metrics, "counter", return_value=counter_mock
        ):
            result = test_function("a", "b", kwarg1="c")

            assert result == "a-b-c"
            counter_mock.inc.assert_called_once()
