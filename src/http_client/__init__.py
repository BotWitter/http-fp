"""http-fp: HTTP client with fingerprint support.

HTTP client with JA3/Akamai fingerprint support for realistic browser requests.
"""

from .client import HTTPClient
from .config import ProxyConfig, BrowserInfo
from .retry import RetryConfig
from .session import SessionManager
from .fingerprint import (
    JA3Generator,
    AkamaiGenerator,
    FingerprintProfile,
    UserAgentGenerator,
)

from . import __version__

__all__ = [
    # Main client
    "HTTPClient",
    # Configuration
    "ProxyConfig",
    "BrowserInfo",
    "RetryConfig",
    "SessionManager",
    # Fingerprinting
    "JA3Generator",
    "AkamaiGenerator",
    "FingerprintProfile",
    "UserAgentGenerator",
    # Version
    "__version__",
]
