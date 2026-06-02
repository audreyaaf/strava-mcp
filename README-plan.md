# Strava MCP — Project Plan

## Project Name
**strava-mcp**

## Vision
Open-source MCP server for Strava so AI clients like Hermes, Claude, Codex, Cursor, Kiro, and OpenClaw can securely connect to a user's Strava account and read training/activity data.

## Core Positioning
`strava-mcp` should be:
- lightweight
- easy to install
- easy to authorize
- cross-platform MCP compatible
- useful for real athlete/workflow questions, not just raw API passthrough

## Strategic Decisions

### 1) Backend approach
Use a **lightweight Python stdio MCP server**.

Why:
- no always-on backend server needed
- no database required for MVP
- no exposed port
- low memory footprint
- easy packaging with `pip` / `uvx`
- easiest path for MCP client compatibility

Architecture:
```text
AI Client
  ↓
MCP client integration
  ↓
strava-mcp (Python stdio process)
  ↓
Strava API
```

Recommended stack:
- Python 3.11+
- official `mcp` Python SDK
- `httpx`
- local token storage using XDG-style config dir
- `pytest` + `ruff`

## 2) Authentication strategy
Goal: user should **not need to manually create a Strava app** for the normal happy path.

Planned auth model:
- package ships with a default Strava app/client configuration
- user runs an auth command
- browser opens
- user clicks authorize
- token is saved locally
- token refresh happens automatically

Desired UX:
```bash
uvx strava-mcp auth
```

Then:
- browser opens
- user approves access
- token saved to local config
- ready to use in MCP clients

Advanced mode should still support custom credentials:
```bash
uvx strava-mcp auth --client-id XXX --client-secret YYY
```

Notes:
- validate whether Strava permits this bundled-app approach cleanly for distributed OSS tooling
- if needed, support PKCE or documented fallback flow
- never require tokens to be pasted into AI chat

## 3) Multi-platform integration target
Primary promise: works across major MCP-capable AI products.

Target platforms:
- Hermes Agent
- Claude Desktop
- Claude Code
- Codex
- Cursor
- Kiro
- OpenClaw

Universal command target:
```bash
uvx strava-mcp
```

Docs should include per-platform config snippets.

## MVP Scope
Keep v0.1 focused.

### MVP capabilities
- OAuth login helper
- local token storage
- auto refresh token
- athlete profile access
- recent activities listing
- single activity detail
- activity streams access
- training summary / recent summary

### Candidate MCP tools
- `get_athlete`
- `list_activities`
- `get_activity`
- `get_activity_streams`
- `summarize_training`

## Nice-to-have after MVP
- weekly summary
- monthly summary
- compare periods
- heart rate analysis
- pace analysis
- training load trend
- gear usage
- segments/clubs support

## Repository Structure
```text
strava-mcp/
├── README.md
├── LICENSE
├── pyproject.toml
├── docs/
│   ├── setup.md
│   ├── auth.md
│   ├── tools-reference.md
│   └── platform-integrations.md
├── examples/
│   ├── hermes-config.yaml
│   ├── claude-desktop-config.json
│   ├── cursor-mcp.json
│   └── codex-config.toml
├── src/
│   └── strava_mcp/
│       ├── __init__.py
│       ├── cli.py
│       ├── server.py
│       ├── auth.py
│       ├── client.py
│       ├── config.py
│       └── tools/
│           ├── athlete.py
│           ├── activities.py
│           ├── streams.py
│           └── analysis.py
└── tests/
    ├── test_auth.py
    ├── test_client.py
    └── test_tools.py
```

## Packaging Strategy
Distribute as:
- `pip install strava-mcp`
- `uvx strava-mcp`

Important:
- CLI should expose auth flow
- MCP server should run cleanly over stdio
- docs should optimize for copy-paste setup

## Security Principles
- never ask users to paste tokens into chat
- store tokens locally only
- support token refresh automatically
- keep secrets out of logs where possible
- document scopes clearly
- minimize requested scopes for MVP while preserving useful functionality

Likely scopes:
- `read`
- `activity:read_all`
- `profile:read_all`

## Open Source Positioning
Recommended license: **MIT**

Potential tagline:
> MCP server for Strava — connect your AI tools to your training data.

Why this project is compelling:
- MCP ecosystem is growing fast
- Strava is recognizable and useful
- AI + quantified-self / fitness is a strong use case
- cross-client support gives broader adoption than a single-platform plugin

## Launch Strategy
Phase 1:
- publish GitHub repo
- clean README
- basic auth flow
- MVP tools
- examples for Hermes / Claude / Cursor / Codex

Phase 2:
- submit to MCP directories
- post on X / Reddit / HN
- collect feedback
- iterate on analysis features

Likely distribution channels:
- GitHub
- MCP directories / listings
- X
- Reddit communities
- Hacker News

## Key Open Questions
1. Can Strava app credentials be safely and acceptably bundled for OSS distribution?
2. Does Strava support the desired auth flow cleanly for local desktop/CLI tooling?
3. Which scopes are strictly required for streams and summaries?
4. Should streams analysis be included in v0.1 or v0.2?
5. Should we support custom app credentials from day one?

## Recommended Immediate Next Steps
1. Create GitHub repo `strava-mcp`
2. Validate Strava OAuth/product constraints
3. Scaffold Python package
4. Implement auth command
5. Implement 3-5 core MCP tools
6. Add platform integration docs
7. Release initial version

## Short Product Summary
`strava-mcp` is planned as a lightweight open-source Python MCP server for Strava with browser-based login, local token storage, auto-refresh, and plug-and-play integration across Hermes, Claude, Cursor, Codex, Kiro, and OpenClaw.
