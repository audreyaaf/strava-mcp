from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "strava-mcp"
STRAVA_API_BASE = "https://www.strava.com/api/v3"
STRAVA_OAUTH_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
STRAVA_OAUTH_TOKEN_URL = "https://www.strava.com/oauth/token"
DEFAULT_REDIRECT_PORT = 8765
DEFAULT_REDIRECT_PATH = "/callback"
DEFAULT_SCOPES = ["read", "activity:read_all", "profile:read_all"]

# Public fallback placeholders. For OSS release, replace these only after validating
# Strava's policy for distributed desktop/CLI apps. Users can always pass custom
# credentials via CLI flags or env vars.
BUNDLED_CLIENT_ID = os.getenv("STRAVA_MCP_CLIENT_ID", "")
BUNDLED_CLIENT_SECRET = os.getenv("STRAVA_MCP_CLIENT_SECRET", "")


def config_dir() -> Path:
    base = os.getenv("XDG_CONFIG_HOME")
    if base:
        return Path(base) / APP_NAME
    return Path.home() / ".config" / APP_NAME


def token_path() -> Path:
    return Path(os.getenv("STRAVA_MCP_TOKEN_PATH", config_dir() / "token.json"))


def credentials_path() -> Path:
    return Path(os.getenv("STRAVA_MCP_CREDENTIALS_PATH", config_dir() / "credentials.json"))


def redirect_uri(port: int = DEFAULT_REDIRECT_PORT) -> str:
    return f"http://localhost:{port}{DEFAULT_REDIRECT_PATH}"
