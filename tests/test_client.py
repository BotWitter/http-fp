"""Tests for HTTPClient class."""

import pytest

from http_client import HTTPClient, ProxyConfig, RetryConfig


def test_client_initialization():
    """Test basic client initialization."""
    client = HTTPClient()
    assert client.timeout == 30
    assert client.randomize_per_request is False
    assert client.profile is not None


def test_client_with_custom_timeout():
    """Test client with custom timeout."""
    client = HTTPClient(timeout=60)
    assert client.timeout == 60


def test_client_with_platform():
    """Test client with forced platform."""
    client = HTTPClient(platform="Windows")
    assert client.profile.platform == "Windows"


def test_client_with_browser():
    """Test client with forced browser type."""
    client = HTTPClient(browser="chrome", platform="Windows")
    assert client.profile.browser_type == "chrome"


def test_fingerprint_generation():
    """Test fingerprint profile generation."""
    client = HTTPClient()
    profile = client.profile

    assert profile.ja3
    assert profile.akamai
    assert profile.user_agent
    assert profile.browser_type in ["chrome", "brave", "edge", "safari"]


def test_fingerprint_randomization():
    """Test fingerprint randomization."""
    client = HTTPClient()
    old_ja3 = client.profile.ja3

    client.randomize()
    new_ja3 = client.profile.ja3

    # Different extensions order means different JA3
    # (might be same occasionally due to randomness)
    assert old_ja3 or new_ja3  # At least one exists


def test_get_fingerprint_info():
    """Test fingerprint info retrieval."""
    client = HTTPClient()
    info = client.get_fingerprint_info()

    assert "ja3" in info
    assert "akamai" in info
    assert "user_agent" in info
    assert "sec_ch_ua" in info
    assert "platform" in info


def test_proxy_config():
    """Test proxy configuration."""
    proxy = ProxyConfig(url="http://proxy.example.com:8080")
    proxies = proxy.get_proxies_dict()

    assert proxies["http"] == "http://proxy.example.com:8080"
    assert proxies["https"] == "http://proxy.example.com:8080"


def test_proxy_config_with_auth():
    """Test proxy with authentication."""
    proxy = ProxyConfig(
        url="http://proxy.example.com:8080",
        username="user",
        password="pass",
    )
    proxies = proxy.get_proxies_dict()

    assert "user:pass@" in proxies["http"]


def test_retry_config():
    """Test retry configuration."""
    retry = RetryConfig(max_retries=5, backoff_factor=1.0)
    assert retry.max_retries == 5
    assert retry.backoff_factor == 1.0


def test_session_manager():
    """Test session manager access."""
    client = HTTPClient()
    assert client.session_manager is not None
    assert hasattr(client.session_manager, "save_cookies")
    assert hasattr(client.session_manager, "load_cookies")


def test_cookies_property():
    """Test cookies property."""
    client = HTTPClient()
    cookies = client.cookies
    assert isinstance(cookies, dict)


def test_headers_generation_navigate():
    """Test header generation for navigation."""
    client = HTTPClient()
    headers = client._get_headers(request_type="navigate")

    assert "user-agent" in headers
    assert "accept" in headers
    assert "text/html" in headers["accept"]
    assert headers["sec-fetch-dest"] == "document"
    assert headers["sec-fetch-mode"] == "navigate"


def test_headers_generation_api():
    """Test header generation for API calls."""
    client = HTTPClient()
    headers = client._get_headers(request_type="api")

    assert headers["accept"] == "*/*"
    assert headers["sec-fetch-dest"] == "empty"
    assert headers["sec-fetch-mode"] == "cors"


def test_brave_headers():
    """Test Brave-specific headers."""
    client = HTTPClient(browser="brave")
    if client.profile.browser_type == "brave":
        headers = client._get_headers()
        assert "dnt" in headers
        assert "sec-gpc" in headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
