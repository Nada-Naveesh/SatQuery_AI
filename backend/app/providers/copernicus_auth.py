"""
SatQuery AI - Copernicus CDSE Authentication Service
Manages OAuth 2.0 Keycloak tokens for the Copernicus Data Space Ecosystem.
Credentials are read strictly from backend environment variables and NEVER exposed to clients.
"""

import os
import time
import logging
import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

TOKEN_ENDPOINT = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


class CopernicusAuth:
    def __init__(self):
        self.client_id = os.environ.get("COPERNICUS_CLIENT_ID", "").strip()
        self.client_secret = os.environ.get("COPERNICUS_CLIENT_SECRET", "").strip()
        self.username = os.environ.get("COPERNICUS_USERNAME", "").strip()
        self.password = os.environ.get("COPERNICUS_PASSWORD", "").strip()
        
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    @property
    def has_credentials(self) -> bool:
        """Returns True if either client credentials or user password credentials are set."""
        return bool(
            (self.client_id and self.client_secret)
            or (self.username and self.password)
        )

    def get_token(self) -> Optional[str]:
        """Retrieves a valid access token, refreshing if expired."""
        if not self.has_credentials:
            return None

        # Return cached token if valid for at least another 60 seconds
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        return self._fetch_new_token()

    def _fetch_new_token(self) -> Optional[str]:
        data: Dict[str, str] = {}
        if self.username and self.password:
            data = {
                "client_id": self.client_id or "cdse-public",
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
            }
            if self.client_secret:
                data["client_secret"] = self.client_secret
        elif self.client_id and self.client_secret:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }
        else:
            return None

        try:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(
                TOKEN_ENDPOINT,
                data=encoded_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "SatQueryAI-SIH2026/2.0"
                }
            )
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    self._access_token = payload.get("access_token")
                    expires_in = payload.get("expires_in", 600)
                    self._token_expires_at = time.time() + float(expires_in)
                    logger.info("Successfully obtained new Copernicus CDSE access token.")
                    return self._access_token
        except Exception as e:
            logger.warning(f"Failed to authenticate with Copernicus CDSE Keycloak: {e}")

        return None


# Global singleton instance
copernicus_auth = CopernicusAuth()
