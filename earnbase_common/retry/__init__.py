"""Retry policies and decorators."""

from datetime import timedelta
from typing import Awaitable, Type, TypeVar, Union, cast

from earnbase_common.logging import get_logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

logger = get_logger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Retry configuration."""

    def __init__(
        self,
        max_attempts: int = 3,
        max_delay: float = 10.0,
        min_delay: float = 1.0,
        exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    ):
        """Initialize retry configuration."""
        self.max_attempts = max_attempts
        self.max_delay = max_delay
        self.min_delay = min_delay
        self.exceptions = exceptions


async def with_retry(
    operation_name: str,
    config: RetryConfig,
    coroutine: Awaitable[T],
) -> T:
    """Execute coroutine with retry policy."""
    retry_policy = AsyncRetrying(
        retry=retry_if_exception_type(config.exceptions),
        stop=(
            stop_after_attempt(config.max_attempts)
            | stop_after_delay(timedelta(seconds=config.max_delay).total_seconds())
        ),
        wait=wait_exponential(
            multiplier=config.min_delay,
            max=config.max_delay,
        ),
        reraise=True,
    )

    try:
        async for attempt in retry_policy:
            with attempt:
                result = await coroutine
                return cast(T, result)
    except RetryError as e:
        logger.error(
            f"{operation_name}_retry_failed",
            max_attempts=config.max_attempts,
            last_exception=str(e.last_attempt.exception()),
        )
        raise e

    raise RuntimeError("This code should never be reached")  # For type checker
