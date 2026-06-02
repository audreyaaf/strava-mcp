# strava-mcp

MCP server for Strava — connect AI agents to your training data.

`strava-mcp` is a lightweight Python stdio MCP server. It lets MCP-capable clients like Hermes, OpenClaw, Claude, Cursor, Codex, and Kiro read Strava athlete/activity data through safe local OAuth token storage.

> Status: MVP scaffold is working locally. OAuth, CLI commands, MCP tools, tests, and lint are in place. Shared bundled OAuth credentials are intentionally not shipped yet.

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
- Standalone CLI helpers:
  - `strava-mcp auth`
  - `strava-mcp summary`
  - `strava-mcp activities`
  - `strava-mcp token-path`

## Install for development

```bash
cd ~/projects/strava-mcp
uv sync --extra dev
uv run strava-mcp --help
```

Validation status:

- `uv run pytest -q` ✅
- `uv run ruff check .` ✅

## Authorize Strava

For now, use your own Strava API credentials while the bundled-app strategy is validated.

1. Create an app at https://www.strava.com/settings/api
2. Set callback domain to `localhost`
3. Run:

```bash
uv run strava-mcp auth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

This opens a browser, receives the local callback, and stores tokens at:

```text
~/.config/strava-mcp/token.json
```

You can also use env vars:

```bash
export STRAVA_MCP_CLIENT_ID=YOUR_CLIENT_ID
export STRAVA_MCP_CLIENT_SECRET=YOUR_CLIENT_SECRET
uv run strava-mcp auth
```

Headless flow:

```bash
uv run strava-mcp auth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --no-browser
```

## Run as MCP server

```bash
uvx strava-mcp
# or from local checkout
uv run strava-mcp
```

No subcommand means stdio MCP server mode.

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
```

## Documentation

- `docs/setup.md`
- `docs/auth.md`
- `docs/tools-reference.md`
- `docs/platform-integrations.md`

## Notes from current review

- OAuth URL generation is correct and uses `http://localhost:8765/callback`.
- State validation is present.
- Token refresh is implemented.
- Tests currently cover config date parsing and summary aggregation, but not live OAuth/network paths yet.
- `pyproject.toml` repository URLs still need final alignment with the chosen GitHub repo slug.

## Roadmap

- Validate public/bundled Strava OAuth app strategy
- Add tests with mocked Strava API responses
- Add better training analysis tools
- Add weekly/monthly summary helpers
- Publish to PyPI
- Submit to MCP directories

## License

MIT
