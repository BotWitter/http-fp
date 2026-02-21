"""Fingerprint profile data class."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class FingerprintProfile:
    """Custom JA3 and Akamai fingerprint profile.

    Attributes:
        ja3: JA3 fingerprint string in format TLSVersion,Ciphers,Extensions,Curves,ECPointFormats
        akamai: Akamai HTTP/2 fingerprint string
        extra_fp: Extra fingerprint options for curl_cffi
        user_agent: Browser User-Agent string
        sec_ch_ua: Sec-CH-UA header value (None for Safari)
        browser_type: Browser type (chrome, brave, edge, safari)
        platform: Operating system platform (Windows, macOS, iOS, Android)
        mobile: Whether this is a mobile device
    """

    ja3: str
    akamai: str
    extra_fp: dict[str, Any]
    user_agent: str
    sec_ch_ua: Optional[str] = None
    sec_ch_ua_mobile: Optional[str] = None
    sec_ch_ua_platform: Optional[str] = None
    accept_language: Optional[str] = None
    browser_type: str = "chrome"
    platform: str = "Windows"
    mobile: bool = False

