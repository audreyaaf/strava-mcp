# strava-mcp

MCP server for Strava — connect AI agents to your training data.

`strava-mcp` is a lightweight Python stdio MCP server. It lets MCP-capable clients like Hermes, OpenClaw, Claude, Cursor, Codex, and Kiro read Strava athlete/activity data through safe local OAuth token storage.

> Status: MVP scaffold is working locally. OAuth, CLI commands, MCP tools, tests, and lint are in place. This project now uses user-owned Strava credentials only.

## Features

- Strava OAuth helper with local callback
- Local token storage in `~/.config/strava-mcp/token.json`
- Automatic access token refresh
- MCP tools:
  - `get_athlete`
  - `list_activities`
  - `get_activity`
  - `get_activity_streams`
  - `summarize_training`
  - `get_recent_activity`
  - `summarize_week`
  - `summarize_month`
  - `compare_weeks`
  - `find_personal_bests`
  - `generate_training_report`
  - `analyze_run_activity`
  - `generate_x_post` (`style`: `santai`, `technical`, `builder`, `personal-progress`)
- Standalone CLI helpers:
  - `strava-mcp auth`
  - `strava-mcp summary`
  - `strava-mcp activities`
  - `strava-mcp token-path`
  - `strava-mcp doctor`
  - `strava-mcp logout`

## Install for development

```bash
cd ~/projects/strava-mcp
uv sync --extra dev
uv run strava-mcp --help
```

Validation status:

- `uv run pytest -q` ✅
- `uv run ruff check .` ✅

## Strava Setup

This MCP server uses user-owned Strava API credentials.

It does not ship shared credentials. Each user must create their own Strava API application.

### Step 1: Create Strava API Application

Open:

https://www.strava.com/settings/api

Create a new API application.

Set:

```text
Authorization Callback Domain = localhost
```

### Step 2: Export Credentials

```bash
export STRAVA_CLIENT_ID="your_client_id"
export STRAVA_CLIENT_SECRET="your_client_secret"
```

Or add them to your environment manager / `.env` file:

```env
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
```

### Step 3: Authenticate

```bash
uv run strava-mcp auth
```

The agent opens Strava login in your browser.

After approval, the token is stored locally:

```text
~/.config/strava-mcp/token.json
```

If you prefer one-off flags, you can still use:

```bash
uv run strava-mcp auth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Headless flow:

```bash
uv run strava-mcp auth --no-browser
```

### Step 4: Start Agent

```bash
uvx strava-mcp
# or from local checkout
uv run strava-mcp
```

No subcommand means stdio MCP server mode.

### Troubleshooting

Check setup:

```bash
uv run strava-mcp doctor
```

Logout:

```bash
uv run strava-mcp logout
```

If login fails, check:

- `STRAVA_CLIENT_ID` is correct
- `STRAVA_CLIENT_SECRET` is correct
- Authorization Callback Domain is exactly `localhost`
- Port `8765` is not already used by another process

## Hermes Agent config

Published package:

```yaml
mcp_servers:
  strava:
    command: "uvx"
    args: ["strava-mcp"]
```

Local development version:

```yaml
mcp_servers:
  strava:
    command: "uv"
    args: ["--directory", "/home/audrey/projects/strava-mcp", "run", "strava-mcp"]
```

Restart Hermes after config changes:

```bash
hermes gateway restart
```

Or test directly:

```bash
hermes mcp test strava
```

## OpenClaw config

Published package:

```yaml
mcp_servers:
  strava:
    command: "uvx"
    args: ["strava-mcp"]
```

Local development version:

```yaml
mcp_servers:
  strava:
    command: "uv"
    args: ["--directory", "/home/audrey/projects/strava-mcp", "run", "strava-mcp"]
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "strava": {
      "command": "uvx",
      "args": ["strava-mcp"]
    }
  }
}
```

## Cursor config

```json
{
  "mcpServers": {
    "strava": {
      "command": "uvx",
      "args": ["strava-mcp"]
    }
  }
}
```

## Codex config

```toml
[mcp_servers.strava]
command = "uvx"
args = ["strava-mcp"]
```

## Kiro config

```json
{
  "mcpServers": {
    "strava": {
      "command": "uvx",
      "args": ["strava-mcp"]
    }
  }
}
```

## CLI examples

```bash
uv run strava-mcp summary --per-page 20
uv run strava-mcp activities --per-page 5
uv run strava-mcp token-path
uv run strava-mcp doctor
uv run strava-mcp logout
```

## Documentation

- `docs/setup.md`
- `docs/auth.md`
- `docs/tools-reference.md`
- `docs/platform-integrations.md`

## Notes from current review

- OAuth URL generation uses `http://localhost:8765/callback`.
- State validation is present.
- Token refresh is implemented.
- Tests cover config date parsing, auth setup copy, and summary aggregation.
- This repo now assumes user-owned Strava OAuth credentials.

## Roadmap

- Add tests with mocked Strava API responses
- Add better training analysis tools
- Add weekly/monthly summary helpers
- Publish to PyPI
- Submit to MCP directories

## License

MIT
