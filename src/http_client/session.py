"""Session management for cookie persistence and state handling.

Provides SessionManager class for saving/loading cookies and
importing/exporting session state.
"""

import json
import logging
from pathlib import Path
from typing import Any

from curl_cffi import requests

logger = logging.getLogger(__name__)


class SessionManager:
    """Manager for HTTP session state persistence.

    Provides methods to save/load cookies and export/import
    complete session state including cookies and headers.
    """

    def __init__(self, session: requests.Session):
        """Initialize session manager.

        Args:
            session: curl_cffi Session instance to manage
        """
        self._session = session

    def save_cookies(self, path: str | Path) -> None:
        """Save session cookies to a file.

        Args:
            path: Path to save cookies (JSON format)
        """
        path = Path(path)
        cookies_dict = {
            cookie.name: {
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires,
                "secure": cookie.secure,
            }
            for cookie in self._session.cookies.jar
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(cookies_dict, f, indent=2)

        logger.debug("Saved %d cookies to %s", len(self._session.cookies), path)

    def load_cookies(self, path: str | Path) -> None:
        """Load cookies from a file into the session.

        Args:
            path: Path to load cookies from (JSON format)
        """
        path = Path(path)
        if not path.exists():
            logger.warning("Cookie file not found: %s", path)
            return

        with path.open("r") as f:
            cookies_dict = json.load(f)

        for name, cookie_data in cookies_dict.items():
            self._session.cookies.set(
                name=name,
                value=cookie_data["value"],
                domain=cookie_data.get("domain", ""),
                path=cookie_data.get("path", "/"),
                secure=cookie_data.get("secure", False),
            )

        logger.debug("Loaded %d cookies from %s", len(cookies_dict), path)

    def export_session(self, path: str | Path) -> None:
        """Export complete session state to a file.

        Args:
            path: Path to save session state (JSON format)
        """
        path = Path(path)

        session_data: dict[str, Any] = {
            "cookies": [
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "expires": cookie.expires,
                    "secure": cookie.secure,
                }
                for cookie in self._session.cookies.jar
            ],
            "headers": dict(self._session.headers),
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(session_data, f, indent=2)

        logger.info("Exported session to %s", path)

    def import_session(self, path: str | Path) -> None:
        """Import session state from a file.

        Args:
            path: Path to load session state from (JSON format)
        """
        path = Path(path)
        if not path.exists():
            logger.warning("Session file not found: %s", path)
            return

        with path.open("r") as f:
            session_data = json.load(f)

        # Load cookies
        for cookie_data in session_data.get("cookies", []):
            self._session.cookies.set(
                name=cookie_data["name"],
                value=cookie_data["value"],
                domain=cookie_data.get("domain", ""),
                path=cookie_data.get("path", "/"),
                secure=cookie_data.get("secure", False),
            )

        # Load headers
        headers = session_data.get("headers", {})
        for key, value in headers.items():
            self._session.headers[key] = value

        logger.info("Imported session from %s", path)

    def clear_cookies(self) -> None:
        """Clear all cookies from the session."""
        self._session.cookies.clear()
        logger.debug("Cleared all cookies")

    def get_cookie_dict(self) -> dict[str, str]:
        """Get all cookies as a dictionary.

        Returns:
            Dictionary mapping cookie names to values
        """
        return {cookie.name: cookie.value for cookie in self._session.cookies.jar}

    def set_cookie(self, name: str, value: str, domain: str = "", **kwargs: Any) -> None:
        """Set a cookie in the session.

        Args:
            name: Cookie name
            value: Cookie value
            domain: Cookie domain
            **kwargs: Additional cookie parameters (path, secure, etc.)
        """
        self._session.cookies.set(
            name=name,
            value=value,
            domain=domain,
            **kwargs,
        )
