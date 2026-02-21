"""Basic usage examples for HTTP Client Fingerprint package."""

from http_client import HTTPClient, ProxyConfig, RetryConfig


def basic_usage():
    """Basic HTTP client usage."""
    print("=== Basic Usage ===")
    client = HTTPClient()

    # Make a simple GET request
    response = client.get("https://httpbin.org/headers")
    print(f"Status: {response.status_code}")
    print(f"Headers received:\n{response.json()}")


def fingerprint_info():
    """Show fingerprint information."""
    print("\n=== Fingerprint Information ===")
    client = HTTPClient()

    info = client.get_fingerprint_info()
    print(f"Browser: {info['platform']} - {info['user_agent'][:50]}...")
    print(f"JA3: {info['ja3'][:80]}...")
    print(f"Akamai: {info['akamai']}")


def custom_browser():
    """Use custom browser and platform."""
    print("\n=== Custom Browser Configuration ===")

    # Chrome on Windows
    client_chrome = HTTPClient(platform="Windows", browser="chrome")
    print(f"Chrome: {client_chrome.profile.user_agent}")

    # Safari on macOS
    client_safari = HTTPClient(platform="macOS", browser="safari")
    print(f"Safari: {client_safari.profile.user_agent}")

    # Chrome on iOS
    client_ios = HTTPClient(platform="iOS", browser="chrome")
    print(f"iOS Chrome: {client_ios.profile.user_agent}")


def proxy_usage():
    """Use proxy configuration."""
    print("\n=== Proxy Configuration ===")

    # From environment (HTTP_PROXY, HTTPS_PROXY)
    client = HTTPClient()
    print(f"Proxy from env: {client.proxy_url}")

    # Manual proxy
    proxy = ProxyConfig(
        url="http://proxy.example.com:8080",
        username="user",
        password="pass",
    )
    # client_proxy = HTTPClient(proxy_config=proxy)
    print(f"Manual proxy configured: {proxy.url}")


def retry_usage():
    """Use retry mechanism."""
    print("\n=== Retry Mechanism ===")

    retry_config = RetryConfig(
        max_retries=3,
        backoff_factor=0.5,
        retry_on_status=[429, 500, 502, 503, 504],
    )

    client = HTTPClient(retry_config=retry_config)
    print(f"Retry config: max_retries={retry_config.max_retries}, "
          f"backoff={retry_config.backoff_factor}")

    # Use retry methods
    try:
        response = client.get_with_retry("https://httpbin.org/status/200")
        print(f"Request successful: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")


def session_management():
    """Manage session state."""
    print("\n=== Session Management ===")

    client = HTTPClient()

    # Make a request that sets cookies
    client.get("https://httpbin.org/cookies/set?session=abc123")

    # Save cookies
    client.session_manager.save_cookies("example_cookies.json")
    print("Cookies saved to example_cookies.json")

    # Export full session
    client.session_manager.export_session("example_session.json")
    print("Session exported to example_session.json")

    # View cookies
    cookies = client.session_manager.get_cookie_dict()
    print(f"Current cookies: {cookies}")

    # Clear cookies
    client.session_manager.clear_cookies()
    print("Cookies cleared")


def randomize_fingerprint():
    """Randomize fingerprint between requests."""
    print("\n=== Fingerprint Randomization ===")

    client = HTTPClient()

    print(f"Initial JA3: {client.profile.ja3[:80]}...")

    # Manually randomize
    client.randomize()
    print(f"After randomize: {client.profile.ja3[:80]}...")

    # Auto-randomize per request
    client_auto = HTTPClient(randomize_per_request=True)
    print("Auto-randomization enabled")


def main():
    """Run all examples."""
    try:
        basic_usage()
        fingerprint_info()
        custom_browser()
        proxy_usage()
        retry_usage()
        session_management()
        randomize_fingerprint()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
