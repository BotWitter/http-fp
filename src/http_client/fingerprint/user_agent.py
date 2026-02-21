"""Browser User-Agent profiles for fingerprint generation.

Supports Windows, macOS, iOS, and Android platforms.
Platform-browser mapping:
  - Windows: Chrome, Brave, Edge
  - macOS:   Chrome, Safari, Brave
  - iOS:     Safari, Chrome (CriOS)
  - Android: Chrome, Brave
"""

import random
from typing import ClassVar, TypedDict


class UserAgentInfo(TypedDict):
    """User-Agent information dictionary."""

    ua: str
    sec_ch_ua: str | None
    platform: str
    mobile: bool


# Platform definitions

PLATFORMS = ["Windows", "macOS", "iOS", "Android"]

PLATFORM_WEIGHTS: dict[str, float] = {
    "Windows": 0.50,
    "iOS": 0.30,
    "Android": 0.20,
    "macOS": 0.20,
}


class UserAgentGenerator:
    """Generator for browser User-Agent strings with matching Sec-CH-UA headers.

    Provides real Chrome/Edge/Brave/Safari User-Agent strings (v141-144)
    across Windows, macOS, iOS, and Android with matching Sec-CH-UA headers.
    """

    PROFILES: ClassVar[list[UserAgentInfo]] = [
        # Windows
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Chromium";v="143", "Not/A)Brand";v="24", "Google Chrome";v="143"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Chromium";v="142", "Not/A)Brand";v="24", "Google Chrome";v="142"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Chromium";v="141", "Not_A Brand";v="24", "Google Chrome";v="141"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Brave";v="143", "Chromium";v="143", "Not/A)Brand";v="24"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Brave";v="142", "Chromium";v="142", "Not/A)Brand";v="24"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
            "sec_ch_ua": '"Chromium";v="143", "Not/A)Brand";v="24", "Microsoft Edge";v="143"',
            "platform": "Windows",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
            "sec_ch_ua": '"Chromium";v="142", "Not/A)Brand";v="24", "Microsoft Edge";v="142"',
            "platform": "Windows",
            "mobile": False,
        },

        # macOS
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "platform": "macOS",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Chromium";v="143", "Not/A)Brand";v="24", "Google Chrome";v="143"',
            "platform": "macOS",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Chromium";v="142", "Not/A)Brand";v="24", "Google Chrome";v="142"',
            "platform": "macOS",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Chromium";v="141", "Not_A Brand";v="24", "Google Chrome";v="141"',
            "platform": "macOS",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Brave";v="143", "Chromium";v="143", "Not/A)Brand";v="24"',
            "platform": "macOS",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/18.3 Safari/605.1.15",
            "sec_ch_ua": None,
            "platform": "macOS",
            "mobile": False,
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/17.6 Safari/605.1.15",
            "sec_ch_ua": None,
            "platform": "macOS",
            "mobile": False,
        },

        # iOS
        {
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1",
            "sec_ch_ua": None,
            "platform": "iOS",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
            "sec_ch_ua": None,
            "platform": "iOS",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/17.7 Mobile/15E148 Safari/604.1",
            "sec_ch_ua": None,
            "platform": "iOS",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) CriOS/144.0.6917.56 Mobile/15E148 Safari/604.1",
            "sec_ch_ua": None,
            "platform": "iOS",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) CriOS/143.0.6917.56 Mobile/15E148 Safari/604.1",
            "sec_ch_ua": None,
            "platform": "iOS",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) CriOS/142.0.6904.80 Mobile/15E148 Safari/604.1",
            "sec_ch_ua": None,
            "platform": "iOS",
            "mobile": True,
        },

        # Android
        {
            "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/144.0.6917.65 Mobile Safari/537.36",
            "sec_ch_ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "platform": "Android",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.6917.65 Mobile Safari/537.36",
            "sec_ch_ua": '"Chromium";v="143", "Not/A)Brand";v="24", "Google Chrome";v="143"',
            "platform": "Android",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.6904.111 Mobile Safari/537.36",
            "sec_ch_ua": '"Chromium";v="142", "Not/A)Brand";v="24", "Google Chrome";v="142"',
            "platform": "Android",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (Linux; Android 15; SM-S936B) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.6917.65 Mobile Safari/537.36",
            "sec_ch_ua": '"Chromium";v="143", "Not/A)Brand";v="24", "Google Chrome";v="143"',
            "platform": "Android",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (Linux; Android 14; SM-S926B) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.6904.111 Mobile Safari/537.36",
            "sec_ch_ua": '"Chromium";v="142", "Not/A)Brand";v="24", "Google Chrome";v="142"',
            "platform": "Android",
            "mobile": True,
        },
        {
            "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.6917.65 Mobile Safari/537.36",
            "sec_ch_ua": '"Brave";v="143", "Chromium";v="143", "Not/A)Brand";v="24"',
            "platform": "Android",
            "mobile": True,
        },
    ]

    @classmethod
    def get_random(cls, platform: str | None = None) -> UserAgentInfo:
        """Get a random User-Agent profile, optionally filtered by platform.

        Args:
            platform: Filter by platform (Windows, macOS, iOS, Android). None = any.

        Returns:
            Dictionary with ua, sec_ch_ua, platform, and mobile keys.
        """
        if platform:
            filtered = [p for p in cls.PROFILES if p["platform"] == platform]
            if filtered:
                return random.choice(filtered)
        return random.choice(cls.PROFILES)

    @classmethod
    def get_weighted_random(cls) -> UserAgentInfo:
        """Get a random User-Agent using realistic platform distribution weights.

        Returns:
            Dictionary with ua, sec_ch_ua, platform, and mobile keys.
        """
        platforms = list(PLATFORM_WEIGHTS.keys())
        weights = list(PLATFORM_WEIGHTS.values())
        chosen_platform = random.choices(platforms, weights=weights, k=1)[0]
        return cls.get_random(platform=chosen_platform)

    @classmethod
    def get_chrome(cls, platform: str | None = None) -> UserAgentInfo:
        """Get a random Chrome User-Agent profile.

        Args:
            platform: Filter by platform. None = any.

        Returns:
            Dictionary with Chrome User-Agent information.
        """
        chrome_profiles = [
            p for p in cls.PROFILES
            if ("Chrome" in p["ua"] or "CriOS" in p["ua"])
            and "Edg" not in p["ua"]
            and "Brave" not in (p.get("sec_ch_ua") or "")
            and (platform is None or p["platform"] == platform)
        ]
        return random.choice(chrome_profiles) if chrome_profiles else cls.get_random(platform)

    @classmethod
    def get_brave(cls, platform: str | None = None) -> UserAgentInfo:
        """Get a random Brave User-Agent profile.

        Args:
            platform: Filter by platform. None = any.

        Returns:
            Dictionary with Brave User-Agent information.
        """
        brave_profiles = [
            p for p in cls.PROFILES
            if "Brave" in (p.get("sec_ch_ua") or "")
            and (platform is None or p["platform"] == platform)
        ]
        return random.choice(brave_profiles) if brave_profiles else cls.get_random(platform)

    @classmethod
    def get_edge(cls, platform: str | None = None) -> UserAgentInfo:
        """Get a random Edge User-Agent profile.

        Args:
            platform: Filter by platform. None = any.

        Returns:
            Dictionary with Edge User-Agent information.
        """
        edge_profiles = [
            p for p in cls.PROFILES
            if "Edg" in p["ua"]
            and (platform is None or p["platform"] == platform)
        ]
        return random.choice(edge_profiles) if edge_profiles else cls.get_random(platform)

    @classmethod
    def get_safari(cls, platform: str | None = None) -> UserAgentInfo:
        """Get a random Safari User-Agent profile.

        Args:
            platform: Filter by platform. None = any.

        Returns:
            Dictionary with Safari User-Agent information.
        """
        safari_profiles = [
            p for p in cls.PROFILES
            if p.get("sec_ch_ua") is None
            and "Safari" in p["ua"]
            and (platform is None or p["platform"] == platform)
        ]
        return random.choice(safari_profiles) if safari_profiles else cls.get_random(platform)

    @classmethod
    def get_version(cls, version: int, platform: str | None = None) -> UserAgentInfo:
        """Get a User-Agent profile for a specific Chrome version.

        Args:
            version: Chrome major version (e.g., 143, 144)
            platform: Filter by platform. None = any.

        Returns:
            Dictionary with User-Agent information for the requested version.
        """
        version_profiles = [
            p for p in cls.PROFILES
            if f"Chrome/{version}" in p["ua"]
            and "Edg" not in p["ua"]
            and "Brave" not in (p.get("sec_ch_ua") or "")
            and (platform is None or p["platform"] == platform)
        ]
        return random.choice(version_profiles) if version_profiles else cls.get_random(platform)
