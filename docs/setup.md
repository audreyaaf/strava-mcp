# Setup

## Requirements

- Python 3.11+
- `uv` for development and `uvx` usage
- A Strava API application for OAuth credentials

## Development install

```bash
git clone git@github.com:audreyaaf/strava-mcp.git
cd strava-mcp
uv sync --extra dev
uv run strava-mcp --help
```

## Strava API app

1. Open https://www.strava.com/settings/api
2. Create an application.
3. Set **Authorization Callback Domain** to:

```text
localhost
```

4. Keep your Client ID and Client Secret private.

## Authorize locally

```bash
uv run strava-mcp auth \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET
```

Headless/server flow:

```bash
uv run strava-mcp auth \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET \
  --no-browser
```

Open the printed URL in your browser. The OAuth callback listens on:

```text
http://localhost:8765/callback
```

Token storage defaults to:

```text
~/.config/strava-mcp/token.json
```

Override paths with:

```bash
export STRAVA_MCP_TOKEN_PATH=/secure/path/token.json
export STRAVA_MCP_CREDENTIALS_PATH=/secure/path/credentials.json
```

## Verify

```bash
uv run strava-mcp activities --per-page 5
uv run strava-mcp summary --per-page 20
```
