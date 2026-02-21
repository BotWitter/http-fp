"""Tests for fingerprint generators."""

import pytest

from http_client.fingerprint import (
    JA3Generator,
    AkamaiGenerator,
    FingerprintProfile,
    UserAgentGenerator,
)


def test_ja3_generation():
    """Test JA3 fingerprint generation."""
    ja3 = JA3Generator.generate(version=143, browser_type="chrome")
    assert ja3
    assert ja3.startswith("771,")  # TLS 1.2

    # Should contain all parts
    parts = ja3.split(",")
    assert len(parts) == 5


def test_ja3_different_versions():
    """Test JA3 with different browser versions."""
    ja3_130 = JA3Generator.generate(version=130)
    ja3_143 = JA3Generator.generate(version=143)

    # Both should be valid
    assert ja3_130 and ja3_143


def test_ja3_extra_fp():
    """Test extra fingerprint options."""
    extra_fp = JA3Generator.get_extra_fp(browser_type="chrome")

    assert "tls_signature_algorithms" in extra_fp
    assert "tls_grease" in extra_fp
    assert extra_fp["tls_permute_extensions"] is False


def test_akamai_generation():
    """Test Akamai fingerprint generation."""
    akamai = AkamaiGenerator.generate(browser_type="chrome")
    assert akamai

    # Format: SETTINGS|WINDOW_UPDATE|PRIORITY|PseudoHeaderOrder
    parts = akamai.split("|")
    assert len(parts) == 4


def test_akamai_safari():
    """Test Akamai fingerprint for Safari."""
    akamai = AkamaiGenerator.generate(browser_type="safari")
    assert "1:4096" in akamai  # Safari-specific header table size


def test_user_agent_get_random():
    """Test random User-Agent generation."""
    ua_info = UserAgentGenerator.get_random()

    assert "ua" in ua_info
    assert "platform" in ua_info
    assert "mobile" in ua_info
    assert ua_info["platform"] in ["Windows", "macOS", "iOS", "Android"]


def test_user_agent_platform_filter():
    """Test User-Agent with platform filter."""
    ua_info = UserAgentGenerator.get_random(platform="Windows")
    assert ua_info["platform"] == "Windows"


def test_user_agent_weighted_random():
    """Test weighted random User-Agent selection."""
    ua_info = UserAgentGenerator.get_weighted_random()
    assert ua_info["platform"] in ["Windows", "iOS", "Android", "macOS"]


def test_user_agent_chrome():
    """Test Chrome User-Agent selection."""
    ua_info = UserAgentGenerator.get_chrome()
    assert "Chrome" in ua_info["ua"] or "CriOS" in ua_info["ua"]
    assert "Edg" not in ua_info["ua"]


def test_user_agent_brave():
    """Test Brave User-Agent selection."""
    ua_info = UserAgentGenerator.get_brave()
    if ua_info.get("sec_ch_ua"):
        assert "Brave" in ua_info["sec_ch_ua"]


def test_user_agent_edge():
    """Test Edge User-Agent selection."""
    ua_info = UserAgentGenerator.get_edge()
    assert "Edg" in ua_info["ua"]


def test_user_agent_safari():
    """Test Safari User-Agent selection."""
    ua_info = UserAgentGenerator.get_safari()
    assert ua_info["sec_ch_ua"] is None
    assert "Safari" in ua_info["ua"]


def test_user_agent_version():
    """Test User-Agent with specific version."""
    ua_info = UserAgentGenerator.get_version(143)
    assert "Chrome/143" in ua_info["ua"]


def test_fingerprint_profile():
    """Test FingerprintProfile dataclass."""
    profile = FingerprintProfile(
        ja3="771,4865-4866,0-10-13,29-23-24,0",
        akamai="1:65536|15663105|0|m,a,s,p",
        extra_fp={},
        user_agent="Mozilla/5.0...",
        browser_type="chrome",
        platform="Windows",
        mobile=False,
    )

    assert profile.ja3
    assert profile.akamai
    assert profile.user_agent
    assert profile.browser_type == "chrome"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
