"""HTTP client with custom JA3/Akamai fingerprint support.

Uses curl_cffi for browser-like TLS handshakes with randomized fingerprints.
"""

import logging
from typing import Any, Optional

from curl_cffi import requests
from curl_cffi.requests import Response

from .config import ProxyConfig, BrowserInfo
from .fingerprint import JA3Generator, AkamaiGenerator, FingerprintProfile
from .retry import RetryConfig, RetryMixin
from .session import SessionManager

logger = logging.getLogger(__name__)


class HTTPClient(RetryMixin):
    """HTTP client with custom JA3 fingerprinting and proxy support.

    Uses curl_cffi Session for browser-like TLS handshakes with unique fingerprints.
    Includes retry logic with exponential backoff and session management.
    """

    def __init__(
        self,
        proxy_config: Optional[ProxyConfig] = None,
        timeout: int = 30,
        randomize_per_request: bool = False,
        platform: Optional[str] = None,
        browser: Optional[str] = None,
        browser_version: Optional[int] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """Initialize the HTTP client.

        Args:
            proxy_config: Optional proxy configuration
            timeout: Request timeout in seconds
            randomize_per_request: Generate new fingerprint for each request
            platform: Force platform (Windows, macOS, iOS, Android). None = weighted random.
            browser: Force browser (chrome, brave, edge, safari). None = random per platform.
            browser_version: Force browser version. None = random.
            retry_config: Optional retry configuration. None = defaults.
        """
        self.timeout = timeout
        self.randomize_per_request = randomize_per_request
        self._platform = platform
        self._browser = browser
        self._browser_version = browser_version
        self._profile: Optional[FingerprintProfile] = None

        self.proxy_config = proxy_config or ProxyConfig.from_env()
        self.proxy_url = self._get_proxy_url()
        self._request_count = 0

        # Create session with fingerprint
        self._session = requests.Session(
            ja3=self.profile.ja3,
            akamai=self.profile.akamai,
            extra_fp=self.profile.extra_fp,
        )

        # Session manager for cookie persistence
        self._session_manager = SessionManager(self._session)

        # Retry configuration
        super().__init__()
        if retry_config:
            self._retry_config = retry_config

        logger.debug(
            "HTTPClient initialized: proxy=%s, timeout=%d, randomize=%s",
            self.proxy_url, timeout, randomize_per_request,
        )

    def _get_proxy_url(self) -> Optional[str]:
        """Convert ProxyConfig to curl_cffi proxy URL format."""
        proxies = self.proxy_config.get_proxies_dict()
        if proxies and "http" in proxies:
            return proxies["http"]
        return None

    @property
    def profile(self) -> FingerprintProfile:
        """Get current fingerprint profile, creating one if needed."""
        if self._profile is None:
            self._profile = self._generate_profile()
        return self._profile

    @property
    def session_manager(self) -> SessionManager:
        """Access session manager for cookie/state persistence."""
        return self._session_manager

    def _generate_profile(self) -> FingerprintProfile:
        """Generate a new fingerprint profile with consistent browser identity.

        All fingerprint components (JA3, Akamai, UA, headers) are derived from
        the same BrowserInfo instance so version/browser type stay consistent.
        """
        browser_info = BrowserInfo.generate(
            platform=self._platform,
            browser=self._browser,
            version=self._browser_version,
        )

        profile = FingerprintProfile(
            ja3=JA3Generator.generate(
                version=browser_info.version,
                browser_type=browser_info.browser_type,
            ),
            akamai=AkamaiGenerator.generate(
                browser_type=browser_info.browser_type,
            ),
            extra_fp=JA3Generator.get_extra_fp(
                browser_type=browser_info.browser_type,
            ),
            user_agent=browser_info.user_agent,
            sec_ch_ua=browser_info.sec_ch_ua,
            sec_ch_ua_mobile=browser_info.sec_ch_ua_mobile,
            sec_ch_ua_platform=f'"{browser_info.platform}"',
            browser_type=browser_info.browser_type,
            platform=browser_info.platform,
            mobile=browser_info.mobile,
        )

        logger.debug(
            "Generated fingerprint: browser=%s v%d platform=%s mobile=%s ja3=%s...",
            browser_info.browser_type, browser_info.version,
            browser_info.platform, browser_info.mobile,
            profile.ja3[:50],
        )
        return profile

    def randomize(self) -> FingerprintProfile:
        """Generate and apply a new random fingerprint profile.

        Recreates the underlying session with the new fingerprint so that
        TLS handshake parameters actually change.

        Returns:
            The newly generated FingerprintProfile
        """
        self._profile = self._generate_profile()

        self._session = requests.Session(
            ja3=self._profile.ja3,
            akamai=self._profile.akamai,
            extra_fp=self._profile.extra_fp,
        )
        self._session_manager = SessionManager(self._session)

        logger.debug("Session recreated with new fingerprint")
        return self._profile

    def _get_headers(
        self,
        extra_headers: Optional[dict[str, str]] = None,
        request_type: str = "navigate",
    ) -> dict[str, str]:
        """Build request headers matching real browser header order.

        Adapts headers based on request_type, browser_type, platform,
        and request count for realistic behavior.

        Args:
            extra_headers: Additional headers to merge
            request_type: 'navigate' for page loads, 'api' for API calls
        """
        headers = {}
        is_navigate = request_type == "navigate"
        is_brave = self.profile.browser_type == "brave"
        is_first_request = self._request_count == 0

        if is_navigate:
            headers["accept"] = (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            )
        else:
            headers["accept"] = "*/*"

        headers["accept-language"] = "en-US,en;q=0.9"
        headers["accept-encoding"] = "gzip, deflate, br, zstd"
        headers["cache-control"] = "no-cache" if is_first_request else "max-age=0"
        headers["pragma"] = "no-cache"

        if is_brave:
            headers["dnt"] = "1"
            headers["sec-gpc"] = "1"

        headers["priority"] = "u=0, i" if is_navigate else "u=1, i"

        if self.profile.sec_ch_ua:
            headers["sec-ch-ua"] = self.profile.sec_ch_ua
            headers["sec-ch-ua-mobile"] = "?1" if self.profile.mobile else "?0"
            headers["sec-ch-ua-platform"] = f'"{self.profile.platform}"'

        if is_navigate:
            headers["sec-fetch-dest"] = "document"
            headers["sec-fetch-mode"] = "navigate"
            headers["sec-fetch-site"] = "none"
            headers["sec-fetch-user"] = "?1"
        else:
            headers["sec-fetch-dest"] = "empty"
            headers["sec-fetch-mode"] = "cors"
            headers["sec-fetch-site"] = "same-site"

        if is_navigate:
            headers["upgrade-insecure-requests"] = "1"

        headers["user-agent"] = self.profile.user_agent

        if extra_headers:
            headers.update(extra_headers)

        self._request_count += 1
        return headers

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
        data: Optional[Any] = None,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        raw_headers: bool = False,
        request_type: str = "navigate",
        **kwargs: Any,
    ) -> Response:
        """Execute HTTP request with custom fingerprint.

        Args:
            raw_headers: If True, use headers as-is without defaults
            request_type: 'navigate' for page loads, 'api' for API calls
        """
        if self.randomize_per_request:
            self.randomize()

        if raw_headers and headers:
            request_headers = headers
        else:
            request_headers = self._get_headers(headers, request_type=request_type)

        logger.debug("Making %s request to %s", method, url)

        response = self._session.request(
            method=method,
            url=url,
            headers=request_headers,
            data=data,
            json=json,
            params=params,
            proxy=self.proxy_url,
            timeout=self.timeout,
            **kwargs,
        )

        return response

    def get(self, url: str, **kwargs: Any) -> Response:
        """Send GET request."""
        return self._make_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        """Send POST request."""
        return self._make_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        """Send PUT request."""
        return self._make_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """Send DELETE request."""
        return self._make_request("DELETE", url, **kwargs)

    def get_with_retry(self, url: str, **kwargs: Any) -> Response:
        """Send GET request with retry logic."""
        return self.request_with_retry(self.get, url, **kwargs)

    def post_with_retry(self, url: str, **kwargs: Any) -> Response:
        """Send POST request with retry logic."""
        return self.request_with_retry(self.post, url, **kwargs)

    def get_fingerprint_info(self) -> dict[str, Any]:
        """Get current fingerprint information."""
        return {
            "ja3": self.profile.ja3,
            "akamai": self.profile.akamai,
            "extra_fp": self.profile.extra_fp,
            "user_agent": self.profile.user_agent,
            "sec_ch_ua": self.profile.sec_ch_ua,
            "platform": self.profile.platform,
        }

    @property
    def cookies(self) -> dict[str, str]:
        """Access session cookies."""
        return dict(self._session.cookies)

    @property
    def client(self) -> requests.Session:
        """Access underlying session for direct requests."""
        return self._session

    @staticmethod
    def _extract_between(
        text: str, start_text: str, end_text: str,
    ) -> Optional[str]:
        """Extract text between two delimiters."""
        try:
            start_index = text.find(start_text)
            if start_index == -1:
                return None
            start_index += len(start_text)
            end_index = text.find(end_text, start_index)
            if end_index == -1:
                return None
            result = text[start_index:end_index]
            return result.replace(" ", "").replace("\n", "")
        except Exception:
            return None
