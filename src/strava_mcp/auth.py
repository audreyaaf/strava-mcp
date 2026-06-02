from __future__ import annotations

import json
import secrets
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import httpx

from .config import (
    BUNDLED_CLIENT_ID,
    BUNDLED_CLIENT_SECRET,
    DEFAULT_REDIRECT_PATH,
    DEFAULT_REDIRECT_PORT,
    DEFAULT_SCOPES,
    STRAVA_OAUTH_AUTHORIZE_URL,
    STRAVA_OAUTH_TOKEN_URL,
    credentials_path,
    redirect_uri,
    token_path,
)


class AuthError(RuntimeError):
    pass


def _write_json_secure(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    try:
        path.chmod(0o600)
    except OSError:
        pass


def save_credentials(client_id: str, client_secret: str) -> None:
    _write_json_secure(
        credentials_path(),
        {"client_id": client_id, "client_secret": client_secret},
    )


def load_credentials() -> tuple[str, str]:
    if credentials_path().exists():
        data = json.loads(credentials_path().read_text())
        return str(data.get("client_id", "")), str(data.get("client_secret", ""))
    return BUNDLED_CLIENT_ID, BUNDLED_CLIENT_SECRET


def save_token(token: dict[str, Any]) -> None:
    _write_json_secure(token_path(), token)


def load_token() -> dict[str, Any]:
    path = token_path()
    if not path.exists():
        raise AuthError(
            "Strava token not found. Run `strava-mcp auth` first, or configure credentials."
        )
    return json.loads(path.read_text())


def build_authorize_url(client_id: str, port: int, scopes: list[str], state: str) -> str:
    query = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri(port),
        "approval_prompt": "force",
        "scope": ",".join(scopes),
        "state": state,
    }
    return f"{STRAVA_OAUTH_AUTHORIZE_URL}?{urllib.parse.urlencode(query)}"


class _CallbackHandler(BaseHTTPRequestHandler):
    server: _OAuthHTTPServer

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if parsed.path != DEFAULT_REDIRECT_PATH:
            self.send_error(404)
            return
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_state = params.get("state", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body><h1>Strava MCP authorized</h1>"
            b"<p>You can close this tab and return to your terminal.</p></body></html>"
        )

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


class _OAuthHTTPServer(HTTPServer):
    auth_code: str | None = None
    auth_state: str | None = None
    auth_error: str | None = None


def exchange_code(client_id: str, client_secret: str, code: str) -> dict[str, Any]:
    response = httpx.post(
        STRAVA_OAUTH_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json()
    save_token(token)
    return token


def refresh_access_token() -> str:
    token = load_token()
    client_id, client_secret = load_credentials()
    if not client_id or not client_secret:
        raise AuthError(
            "Missing Strava client credentials. Run `strava-mcp auth --client-id ...`."
        )

    response = httpx.post(
        STRAVA_OAUTH_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
        timeout=30,
    )
    response.raise_for_status()
    new_token = response.json()
    save_token(new_token)
    return str(new_token["access_token"])


def get_access_token() -> str:
    token = load_token()
    expires_at = int(token.get("expires_at", 0))
    if expires_at > int(time.time()) + 60:
        return str(token["access_token"])
    return refresh_access_token()


def run_auth_flow(
    client_id: str | None = None,
    client_secret: str | None = None,
    port: int = DEFAULT_REDIRECT_PORT,
    scopes: list[str] | None = None,
    open_browser: bool = True,
) -> dict[str, Any]:
    saved_id, saved_secret = load_credentials()
    client_id = client_id or saved_id
    client_secret = client_secret or saved_secret
    scopes = scopes or DEFAULT_SCOPES

    if not client_id or not client_secret:
        raise AuthError(
            "Missing Strava app credentials. For now run: "
            "strava-mcp auth --client-id YOUR_ID --client-secret YOUR_SECRET"
        )

    save_credentials(client_id, client_secret)
    state = secrets.token_urlsafe(24)
    url = build_authorize_url(client_id, port, scopes, state)

    server = _OAuthHTTPServer(("localhost", port), _CallbackHandler)
    print(f"Open this URL to authorize Strava MCP:\n{url}\n")
    if open_browser:
        webbrowser.open(url)

    while not server.auth_code and not server.auth_error:
        server.handle_request()

    if server.auth_error:
        raise AuthError(f"Strava authorization failed: {server.auth_error}")
    if server.auth_state != state:
        raise AuthError("OAuth state mismatch. Please retry auth.")
    if not server.auth_code:
        raise AuthError("No authorization code received.")

    return exchange_code(client_id, client_secret, server.auth_code)
