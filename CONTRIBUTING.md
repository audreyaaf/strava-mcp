# Contributing

Thanks for helping improve `strava-mcp`.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Principles

- Keep the MCP server lightweight.
- Do not log OAuth tokens or secrets.
- Prefer small, focused MCP tools over large magical endpoints.
- Add tests for client, auth, and analysis behavior.
