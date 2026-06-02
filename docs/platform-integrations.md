# Platform Integrations

Run auth once before using the MCP server in a client:

```bash
uvx --from /home/audrey/projects/strava-mcp strava-mcp auth \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET
```

For published package usage, replace the local `uvx --from ...` command with `uvx strava-mcp`.

## Hermes Agent

Local development config:

```yaml
mcp_servers:
  strava:
    command: "uv"
    args: ["--directory", "/home/audrey/projects/strava-mcp", "run", "strava-mcp"]
    connect_timeout: 60
    timeout: 120
```

Published package config:

```yaml
mcp_servers:
  strava:
    command: "uvx"
    args: ["strava-mcp"]
```

Then restart Hermes:

```bash
hermes gateway restart
```

Or test directly:

```bash
hermes mcp test strava
```

## OpenClaw

```yaml
mcp_servers:
  strava:
    command: "uv"
    args: ["--directory", "/home/audrey/projects/strava-mcp", "run", "strava-mcp"]
```

## Claude Desktop

```json
{
  "mcpServers": {
    "strava": {
      "command": "uv",
      "args": ["--directory", "/home/audrey/projects/strava-mcp", "run", "strava-mcp"]
    }
  }
}
```

## Codex

```toml
[mcp_servers.strava]
command = "uv"
args = ["--directory", "/home/audrey/projects/strava-mcp", "run", "strava-mcp"]
```

## Smoke test

A successful MCP client should discover these tools:

- `get_athlete`
- `list_activities`
- `get_activity`
- `get_activity_streams`
- `summarize_training`
