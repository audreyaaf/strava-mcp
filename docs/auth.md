# Authentication

`strava-mcp` uses Strava OAuth and stores tokens locally. Tokens are never printed by the CLI and should never be pasted into AI chat.

## OAuth flow

1. `strava-mcp auth` builds a Strava authorization URL.
2. It starts a local HTTP callback server on `localhost:8765`.
3. You approve the requested scopes in the browser.
4. Strava redirects to `http://localhost:8765/callback?code=...&state=...`.
5. The CLI validates the OAuth `state` value.
6. The CLI exchanges the authorization code for tokens.
7. Tokens are written to `~/.config/strava-mcp/token.json` with `0600` permissions where supported.

## Required credentials

For the current MVP, provide your own Strava API app credentials:

```bash
uv run strava-mcp auth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Or use env vars:

```bash
export STRAVA_MCP_CLIENT_ID=YOUR_CLIENT_ID
export STRAVA_MCP_CLIENT_SECRET=YOUR_CLIENT_SECRET
uv run strava-mcp auth
```

Bundled public app credentials are intentionally not included yet. Strava's policy for distributed CLI/desktop OAuth apps should be validated before shipping a shared app credential.

## Scopes

Default scopes:

- `read`
- `activity:read_all`
- `profile:read_all`

These support athlete profile reads, activity listing, activity details, streams, and summaries.

Customize scopes by repeating `--scope`:

```bash
uv run strava-mcp auth \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET \
  --scope read \
  --scope activity:read_all
```

## Token refresh

When an access token is near expiry, `strava-mcp` refreshes it using the saved refresh token and credentials.

## Security notes

- Do not commit `token.json` or `credentials.json`.
- Do not paste tokens or secrets into prompts.
- Use a dedicated Strava API app for development.
- Keep the callback domain set to `localhost`.
