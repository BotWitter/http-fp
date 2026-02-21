"""Akamai HTTP/2 fingerprint generator with browser-aware randomization.

Generates Akamai fingerprints that match real Chromium-based browser
HTTP/2 settings with high variation for uniqueness.

Reference:
    https://curl-cffi.readthedocs.io/en/latest/impersonate/customize.html
"""

import random
from typing import ClassVar


class AkamaiGenerator:
    """Browser-aware Akamai HTTP/2 fingerprint generator with high uniqueness.

    Generates Akamai fingerprints with realistic variation:
    - Browser-specific SETTINGS frames
    - Randomized WINDOW_UPDATE within real Chrome range
    - Variable MAX_CONCURRENT_STREAMS inclusion
    - Randomized priority weight

    Format: SETTINGS|WINDOW_UPDATE|PRIORITY|PseudoHeaderOrder
    
    Uniqueness: ~500+ combinations
    """

    # SETTINGS frame components
    # 1: HEADER_TABLE_SIZE (always 65536)
    # 2: ENABLE_PUSH (0 for Chrome/Brave, omitted for Edge)
    # 3: MAX_CONCURRENT_STREAMS (optional, 100-1000)
    # 4: INITIAL_WINDOW_SIZE (always 6291456)
    # 6: MAX_HEADER_LIST_SIZE (always 262144)
    
    # Real Chrome WINDOW_UPDATE values observed in the wild (expanded range)
    WINDOW_UPDATE_VALUES: ClassVar[list[int]] = [
        15663105, 15728640, 15794175, 15859710, 15925245,
        15990780, 16056315, 16121850, 16187385, 16252920,
    ]
    
    # Priority values (0 is most common but others seen)
    PRIORITY_VALUES: ClassVar[list[str]] = ["0", "0", "0", "1", "3"]
    
    # Pseudo header orders seen in the wild
    PSEUDO_HEADER_ORDERS: ClassVar[list[str]] = [
        "m,a,s,p",  # Most common: method, authority, scheme, path
        "m,s,a,p",  # Alternate order
        "m,p,a,s",  # Another variant
    ]

    @classmethod
    def _generate_settings(cls, browser_type: str) -> str:
        """Generate SETTINGS frame based on browser type."""
        # Base settings all browsers have
        header_table_size = "1:65536"
        initial_window_size = "4:6291456"
        max_header_list_size = "6:262144"
        
        # Safari uses different HTTP/2 settings
        if browser_type == "safari":
            return "1:4096;4:4194304;6:262144"
        
        # ENABLE_PUSH - Chrome/Brave include it, Edge omits
        enable_push = "2:0" if browser_type in ["chrome", "brave"] else None
        
        # MAX_CONCURRENT_STREAMS - randomly included
        max_concurrent = None
        if random.random() < 0.4:  # 40% chance to include
            max_concurrent = f"3:{random.choice([100, 200, 500, 1000])}"
        
        # Build settings string
        parts = [header_table_size]
        if enable_push:
            parts.append(enable_push)
        if max_concurrent:
            parts.append(max_concurrent)
        parts.extend([initial_window_size, max_header_list_size])
        
        return ";".join(parts)

    @classmethod
    def generate(cls, browser_type: str = "chrome") -> str:
        """Generate browser-aware Akamai HTTP/2 fingerprint.

        Args:
            browser_type: Browser type (chrome, brave, edge)

        Returns:
            Akamai fingerprint string: SETTINGS|WINDOW_UPDATE|PRIORITY|PseudoHeaderOrder
        """
        settings = cls._generate_settings(browser_type)
        window_update = random.choice(cls.WINDOW_UPDATE_VALUES)
        priority = random.choice(cls.PRIORITY_VALUES)
        pseudo_order = random.choice(cls.PSEUDO_HEADER_ORDERS)

        return f"{settings}|{window_update}|{priority}|{pseudo_order}"
