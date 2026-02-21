"""Retry mechanism with exponential backoff for HTTP requests.

Provides RetryConfig and RetryMixin for handling transient failures
with configurable retry policies.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from curl_cffi.requests import Response

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for request retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff delay
        retry_on_status: HTTP status codes that trigger retry
        retry_on_timeout: Whether to retry on timeout errors
        jitter: Whether to add random jitter to backoff delays
    """

    max_retries: int = 3
    backoff_factor: float = 0.5
    retry_on_status: list[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )
    retry_on_timeout: bool = True
    jitter: bool = True

    def should_retry(self, response: Response | None, exception: Exception | None) -> bool:
        """Determine if request should be retried.

        Args:
            response: HTTP response (None if exception occurred)
            exception: Exception that occurred (None if response received)

        Returns:
            True if request should be retried
        """
        if exception:
            return self.retry_on_timeout
        if response and response.status_code in self.retry_on_status:
            return True
        return False

    def get_backoff_time(self, attempt: int) -> float:
        """Calculate backoff delay before next retry.

        Args:
            attempt: Current retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.backoff_factor * (2 ** attempt)
        if self.jitter:
            import random

            delay = delay * (0.5 + random.random() * 0.5)
        return delay


class RetryMixin:
    """Mixin class for adding retry capability to HTTP clients.

    Provides request_with_retry method that wraps request functions
    with exponential backoff retry logic.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._retry_config = RetryConfig()

    @property
    def retry_config(self) -> RetryConfig:
        """Get current retry configuration."""
        return self._retry_config

    def set_retry_config(
        self,
        max_retries: int | None = None,
        backoff_factor: float | None = None,
        retry_on_status: list[int] | None = None,
        retry_on_timeout: bool | None = None,
    ) -> None:
        """Update retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplier for exponential backoff
            retry_on_status: HTTP status codes that trigger retry
            retry_on_timeout: Whether to retry on timeout errors
        """
        if max_retries is not None:
            self._retry_config.max_retries = max_retries
        if backoff_factor is not None:
            self._retry_config.backoff_factor = backoff_factor
        if retry_on_status is not None:
            self._retry_config.retry_on_status = retry_on_status
        if retry_on_timeout is not None:
            self._retry_config.retry_on_timeout = retry_on_timeout

    def request_with_retry(
        self,
        request_func: Callable[..., Response],
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """Execute request with retry logic.

        Args:
            request_func: Function to execute (e.g., session.get)
            *args: Positional arguments for request function
            **kwargs: Keyword arguments for request function

        Returns:
            Response object

        Raises:
            Last exception if all retries are exhausted
        """
        last_exception: Exception | None = None
        last_response: Response | None = None

        for attempt in range(self._retry_config.max_retries + 1):
            try:
                response = request_func(*args, **kwargs)
                if self._retry_config.should_retry(response, None):
                    if attempt < self._retry_config.max_retries:
                        backoff = self._retry_config.get_backoff_time(attempt)
                        logger.warning(
                            "Request returned status %d, retrying in %.2fs (attempt %d/%d)",
                            response.status_code,
                            backoff,
                            attempt + 1,
                            self._retry_config.max_retries,
                        )
                        time.sleep(backoff)
                        continue
                return response
            except Exception as e:
                last_exception = e
                if self._retry_config.should_retry(None, e):
                    if attempt < self._retry_config.max_retries:
                        backoff = self._retry_config.get_backoff_time(attempt)
                        logger.warning(
                            "Request failed with %s, retrying in %.2fs (attempt %d/%d)",
                            type(e).__name__,
                            backoff,
                            attempt + 1,
                            self._retry_config.max_retries,
                        )
                        time.sleep(backoff)
                        continue
                raise

        # All retries exhausted
        if last_exception:
            raise last_exception
        if last_response:
            return last_response
        raise RuntimeError("All retries exhausted without response")
