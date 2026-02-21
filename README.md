# http-fp

HTTP client with JA3/Akamai fingerprint support for realistic browser requests.

## Features

- **JA3 Fingerprinting**: Customizable TLS fingerprints with manual extension permutation
- **Akamai Fingerprinting**: Browser-aware HTTP/2 fingerprint generation
- **Realistic User-Agents**: Pre-defined profiles for Chrome, Brave, Edge, and Safari
- **Proxy Support**: Flexible proxy configuration with environment variable support
- **Retry Logic**: Configurable exponential backoff retry mechanism
- **Session Management**: Cookie persistence and session state import/export
- **Platform Support**: Windows, macOS, iOS, and Android profiles

## Installation

```bash
pip install http-fp
```

## Quick Start

```python
from http_client import HTTPClient

# Basic usage
client = HTTPClient()
response = client.get("https://httpbin.org/headers")
print(response.json())
```

## Configuration

### Proxy Configuration

```python
from http_client import HTTPClient, ProxyConfig

# From environment variables (HTTP_PROXY, HTTPS_PROXY)
client = HTTPClient()

# Manual configuration
proxy = ProxyConfig(url="http://proxy.example.com:8080")
client = HTTPClient(proxy_config=proxy)

# With authentication
proxy = ProxyConfig(
    url="http://proxy.example.com:8080",
    username="user",
    password="pass"
)
client = HTTPClient(proxy_config=proxy)
```

### Browser Fingerprinting

```python
from http_client import HTTPClient

# Force specific platform and browser
client = HTTPClient(
    platform="Windows",  # Windows, macOS, iOS, Android
    browser="chrome",    # chrome, brave, edge, safari
    browser_version=143,
)

# Randomize fingerprint for each request
client = HTTPClient(randomize_per_request=True)

# Manually randomize fingerprint
client.randomize()
```

### Retry Configuration

```python
from http_client import HTTPClient, RetryConfig

retry_config = RetryConfig(
    max_retries=5,
    backoff_factor=1.0,
    retry_on_status=[429, 500, 502, 503, 504],
)

client = HTTPClient(retry_config=retry_config)

# Or configure after initialization
client.set_retry_config(max_retries=3)

# Use retry methods
response = client.get_with_retry("https://example.com")
```

### Session Management

```python
from http_client import HTTPClient

client = HTTPClient()

# Save cookies
client.session_manager.save_cookies("cookies.json")

# Load cookies
client.session_manager.load_cookies("cookies.json")

# Export full session state
client.session_manager.export_session("session_state.json")

# Import session state
client.session_manager.import_session("session_state.json")

# Clear cookies
client.session_manager.clear_cookies()

# Access cookies
cookies = client.session_manager.get_cookie_dict()
```

## Fingerprint Information

View current fingerprint details:

```python
client = HTTPClient()
info = client.get_fingerprint_info()
print(f"JA3: {info['ja3']}")
print(f"Akamai: {info['akamai']}")
print(f"User-Agent: {info['user_agent']}")
```

## License

MIT License
