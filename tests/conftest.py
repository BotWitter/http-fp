"""Test fixtures and configuration for pytest."""

import pytest

from http_client import HTTPClient, ProxyConfig


@pytest.fixture
def client():
    """Create HTTP client instance for testing."""
    return HTTPClient(timeout=10)


@pytest.fixture
def client_with_retry():
    """Create HTTP client with retry enabled."""
    from http_client import RetryConfig

    retry_config = RetryConfig(max_retries=2, backoff_factor=0.1)
    return HTTPClient(timeout=10, retry_config=retry_config)


@pytest.fixture
def proxy_config():
    """Create proxy configuration."""
    return ProxyConfig(url="http://proxy.example.com:8080")
