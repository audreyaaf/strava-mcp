# strava-mcp

MCP server for Strava — connect AI agents to your training data.

`strava-mcp` is a lightweight Python stdio MCP server. It lets MCP-capable clients like Hermes, OpenClaw, Claude, Cursor, Codex, and Kiro read Strava athlete/activity data through safe local OAuth token storage.

> Status: early MVP scaffold. Auth and core tools are implemented, but bundled OAuth app credentials still need policy validation before public release.

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

## Install for development

```bash
cd ~/projects/strava-mcp
uv sync --extra dev
uv run strava-mcp --help
```

## Authorize Strava

For now, use custom Strava API credentials while the public bundled-app strategy is validated.

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

## Run as MCP server

```bash
uvx strava-mcp
# or from local checkout
uv run strava-mcp
```

No subcommand means stdio MCP server mode.

## Hermes Agent config

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

## OpenClaw config

```yaml
mcp_servers:
  strava:
    command: "uvx"
    args: ["strava-mcp"]
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

## Roadmap

- Validate public/bundled Strava OAuth app strategy
- Add tests with mocked Strava API responses
- Add better training analysis tools
- Add weekly/monthly summary helpers
- Publish to PyPI
- Submit to MCP directories

## License

MIT
