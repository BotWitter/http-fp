"""JA3 fingerprint generator with browser-aware TLS configuration.

Generates unique JA3 fingerprints based on browser type and version.
Implements manual extension permutation for maximum uniqueness since
curl_cffi's native permutation is limited.

Reference:
    https://curl-cffi.readthedocs.io/en/latest/impersonate/customize.html
"""

import random
from typing import Any, ClassVar


class JA3Generator:
    """Browser-aware JA3 fingerprint generator with high uniqueness.

    Generates unique JA3 fingerprints by combining:
    - Multiple Chrome version support (130-143)
    - Manual extension permutation (not relying on curl_cffi)
    - Optional GREASE value injection
    - Browser-type aware signature algorithms
    
    Uniqueness: ~10000+ combinations per browser type
    """

    TLS_VERSION: ClassVar[str] = "771"  # TLS 1.2

    # Cipher suites - standard Chromium cipher order
    CIPHERS: ClassVar[str] = "4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53"

    # Base extensions that all versions share (order will be randomized)
    BASE_EXTENSIONS: ClassVar[list[str]] = [
        "0",      # server_name
        "5",      # status_request
        "10",     # supported_groups
        "11",     # ec_point_formats
        "13",     # signature_algorithms
        "16",     # application_layer_protocol_negotiation
        "18",     # signed_certificate_timestamp
        "23",     # extended_master_secret
        "27",     # compress_certificate
        "35",     # session_ticket
        "43",     # supported_versions
        "45",     # psk_key_exchange_modes
        "51",     # key_share
        "65037",  # encrypted_client_hello (outer)
        "65281",  # renegotiation_info
    ]
    
    # ECH extension (17613) - added in Chrome 117+
    ECH_EXTENSION: ClassVar[str] = "17613"

    # Curve sets by version range
    CURVE_SETS: ClassVar[dict[str, str]] = {
        "old": "29-23-24",                    # Chrome < 130
        "kyber": "4588-29-23-24",             # Chrome 130+ with X25519Kyber768
    }

    EC_POINT_FORMATS: ClassVar[str] = "0"

    # Signature algorithms per browser type
    SIGNATURE_ALGORITHMS: ClassVar[dict[str, list[str]]] = {
        "chrome": [
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256",
            "rsa_pkcs1_sha256",
            "ecdsa_secp384r1_sha384",
            "rsa_pss_rsae_sha384",
            "rsa_pkcs1_sha384",
            "rsa_pss_rsae_sha512",
            "rsa_pkcs1_sha512",
        ],
        "brave": [
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256",
            "rsa_pkcs1_sha256",
            "ecdsa_secp384r1_sha384",
            "rsa_pss_rsae_sha384",
            "rsa_pkcs1_sha384",
            "rsa_pss_rsae_sha512",
            "rsa_pkcs1_sha512",
        ],
        "edge": [
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256",
            "rsa_pkcs1_sha256",
            "ecdsa_secp384r1_sha384",
            "rsa_pss_rsae_sha384",
            "rsa_pkcs1_sha384",
            "rsa_pss_rsae_sha512",
            "rsa_pkcs1_sha512",
        ],
    }

    @classmethod
    def _permute_extensions(cls, extensions: list[str]) -> list[str]:
        """Randomly permute extensions for uniqueness."""
        ext_copy = extensions.copy()
        random.shuffle(ext_copy)
        return ext_copy

    @classmethod
    def generate(
        cls,
        version: int = 143,
        browser_type: str = "chrome",
    ) -> str:
        """Generate a unique JA3 fingerprint string.

        Manual extension permutation provides much higher uniqueness
        than curl_cffi's native permutation.

        Args:
            version: Chrome major version (130-143)
            browser_type: Browser type (chrome, brave, edge)

        Returns:
            JA3 string: TLSVersion,Ciphers,Extensions,Curves,ECPointFormats
        """
        # Build extension list based on version
        extensions = cls.BASE_EXTENSIONS.copy()
        
        # Add ECH for Chrome 117+
        if version >= 117:
            extensions.append(cls.ECH_EXTENSION)
        
        # Permute extensions for uniqueness
        extensions = cls._permute_extensions(extensions)
        
        # Select curves based on version
        if version >= 130:
            curves = cls.CURVE_SETS["kyber"]
        else:
            curves = cls.CURVE_SETS["old"]
        
        ext_str = "-".join(extensions)
        
        return f"{cls.TLS_VERSION},{cls.CIPHERS},{ext_str},{curves},{cls.EC_POINT_FORMATS}"

    @classmethod
    def get_extra_fp(cls, browser_type: str = "chrome") -> dict[str, Any]:
        """Get extra fingerprint options for curl_cffi.

        We disable curl_cffi's native permutation since we do it manually
        for better control and uniqueness.

        Args:
            browser_type: Browser type for signature algorithm selection

        Returns:
            Dictionary for curl_cffi extra_fp parameter.
        """
        sig_algs = cls.SIGNATURE_ALGORITHMS.get(
            browser_type, cls.SIGNATURE_ALGORITHMS["chrome"]
        )
        
        # Randomize http2 stream weight slightly for more uniqueness
        stream_weight = random.choice([220, 230, 240, 250, 256])
        
        return {
            "tls_signature_algorithms": sig_algs,
            "tls_grease": True,  # GREASE values like real Chrome
            "tls_permute_extensions": False,  # We do manual permutation
            "tls_cert_compression": "brotli",
            "http2_stream_weight": stream_weight,
            "http2_stream_exclusive": 1,
        }
