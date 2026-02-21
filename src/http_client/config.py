"""Configuration classes for HTTP client.

Provides ProxyConfig and BrowserInfo classes for managing proxy settings
and browser identity generation.
"""

import os
import random
import re
from dataclasses import dataclass
from typing import Optional

from .fingerprint.user_agent import UserAgentGenerator


@dataclass
class ProxyConfig:
    """Proxy configuration for HTTP requests.

    Attributes:
        url: Proxy URL (e.g., "http://proxy.example.com:8080")
        username: Optional proxy username
        password: Optional proxy password
    """

    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ProxyConfig":
        """Create ProxyConfig from environment variables.

        Reads from HTTP_PROXY, HTTPS_PROXY, or http_proxy environment variables.
        Supports URLs with embedded credentials: http://user:pass@host:port

        Returns:
            ProxyConfig instance with settings from environment
        """
        proxy_url = (
            os.environ.get("HTTPS_PROXY")
            or os.environ.get("HTTP_PROXY")
            or os.environ.get("https_proxy")
            or os.environ.get("http_proxy")
        )

        if not proxy_url:
            return cls()

        # Parse credentials from URL if present
        # Format: http://username:password@host:port
        match = re.match(
            r"^(https?://)?(?:([^:]+):([^@]+)@)?(.+)$", proxy_url
        )
        if match:
            protocol, username, password, host = match.groups()
            protocol = protocol or "http://"
            return cls(
                url=f"{protocol}{host}",
                username=username,
                password=password,
            )

        return cls(url=proxy_url)

    def get_proxies_dict(self) -> dict[str, str]:
        """Get proxy configuration as dictionary for curl_cffi.

        Returns:
            Dictionary with 'http' and 'https' proxy URLs.
            Empty dict if no proxy is configured.
        """
        if not self.url:
            return {}

        proxy_url = self.url
        if self.username and self.password:
            # Insert credentials into URL
            if "://" in proxy_url:
                protocol, rest = proxy_url.split("://", 1)
                proxy_url = f"{protocol}://{self.username}:{self.password}@{rest}"
            else:
                proxy_url = f"http://{self.username}:{self.password}@{proxy_url}"

        return {
            "http": proxy_url,
            "https": proxy_url,
        }


@dataclass
class BrowserInfo:
    """Browser identity information for fingerprinting.

    Attributes:
        version: Browser major version (e.g., 143)
        browser_type: Browser type (chrome, brave, edge, safari)
        user_agent: Full User-Agent string
        sec_ch_ua: Sec-CH-UA header value (None for Safari)
        sec_ch_ua_mobile: Sec-CH-UA-Mobile header value
        platform: Operating system platform
        mobile: Whether this is a mobile device
    """

    version: int
    browser_type: str
    user_agent: str
    sec_ch_ua: Optional[str]
    sec_ch_ua_mobile: str
    platform: str
    mobile: bool

    @classmethod
    def generate(
        cls,
        platform: Optional[str] = None,
        browser: Optional[str] = None,
        version: Optional[int] = None,
    ) -> "BrowserInfo":
        """Generate consistent browser identity using UserAgentGenerator.

        Args:
            platform: Force platform (Windows, macOS, iOS, Android). None = weighted random.
            browser: Force browser (chrome, brave, edge, safari). None = random per platform.
            version: Force browser version. None = random.

        Returns:
            BrowserInfo with consistent browser identity across all components
        """
        if version is not None and browser is not None:
            # Specific version requested
            if browser == "chrome":
                ua_info = UserAgentGenerator.get_version(version, platform)
            elif browser == "brave":
                ua_info = UserAgentGenerator.get_brave(platform)
            elif browser == "edge":
                ua_info = UserAgentGenerator.get_edge(platform)
            elif browser == "safari":
                ua_info = UserAgentGenerator.get_safari(platform)
            else:
                ua_info = UserAgentGenerator.get_random(platform)
        elif browser is not None:
            # Specific browser requested
            if browser == "chrome":
                ua_info = UserAgentGenerator.get_chrome(platform)
            elif browser == "brave":
                ua_info = UserAgentGenerator.get_brave(platform)
            elif browser == "edge":
                ua_info = UserAgentGenerator.get_edge(platform)
            elif browser == "safari":
                ua_info = UserAgentGenerator.get_safari(platform)
            else:
                ua_info = UserAgentGenerator.get_random(platform)
        elif platform is not None:
            # Specific platform requested
            ua_info = UserAgentGenerator.get_random(platform)
        else:
            # Fully random with platform weights
            ua_info = UserAgentGenerator.get_weighted_random()

        # Extract browser type and version from UA string
        browser_type = cls._detect_browser_type(ua_info["ua"], ua_info.get("sec_ch_ua"))
        version_num = cls._extract_version(ua_info["ua"], browser_type)

        return cls(
            version=version_num,
            browser_type=browser_type,
            user_agent=ua_info["ua"],
            sec_ch_ua=ua_info["sec_ch_ua"],
            sec_ch_ua_mobile="?1" if ua_info["mobile"] else "?0",
            platform=ua_info["platform"],
            mobile=ua_info["mobile"],
        )

    @staticmethod
    def _detect_browser_type(ua: str, sec_ch_ua: Optional[str]) -> str:
        """Detect browser type from User-Agent and Sec-CH-UA headers."""
        if sec_ch_ua:
            if "Brave" in sec_ch_ua:
                return "brave"
            if "Edge" in sec_ch_ua or "Edg" in ua:
                return "edge"
            if "Chrome" in sec_ch_ua:
                return "chrome"
        if "Safari" in ua and "Chrome" not in ua and "Edg" not in ua:
            return "safari"
        if "Edg" in ua:
            return "edge"
        return "chrome"

    @staticmethod
    def _extract_version(ua: str, browser_type: str) -> int:
        """Extract browser major version from User-Agent string."""
        patterns = {
            "chrome": r"Chrome/(\d+)",
            "brave": r"Chrome/(\d+)",
            "edge": r"Edg/(\d+)",
            "safari": r"Version/(\d+)",
        }
        pattern = patterns.get(browser_type, r"Chrome/(\d+)")
        match = re.search(pattern, ua)
        return int(match.group(1)) if match else 143
