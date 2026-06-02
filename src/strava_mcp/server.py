from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import tools
from .auth import AuthError, load_token, run_auth_flow

mcp = FastMCP("strava-mcp")


@mcp.tool()
def get_athlete() -> dict[str, Any]:
    """Get authenticated Strava athlete profile."""
    return tools.get_athlete()


@mcp.tool()
def list_activities(
    per_page: int = 10,
    page: int = 1,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """List recent Strava activities. Optional after/before are ISO datetime strings."""
    return tools.list_activities(per_page=per_page, page=page, after=after, before=before)


@mcp.tool()
def get_activity(activity_id: int, include_all_efforts: bool = False) -> dict[str, Any]:
    """Get detailed Strava activity by ID."""
    return tools.get_activity(activity_id=activity_id, include_all_efforts=include_all_efforts)


@mcp.tool()
def get_activity_streams(activity_id: int, keys: list[str] | None = None) -> Any:
    """Get activity stream data like time, distance, GPS, HR, cadence, power."""
    return tools.get_activity_streams(activity_id=activity_id, keys=keys)


@mcp.tool()
def summarize_training(
    per_page: int = 20,
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    """Summarize recent Strava activities."""
    return tools.summarize_training(per_page=per_page, after=after, before=before)


def ensure_auth_ready() -> None:
    try:
        load_token()
    except AuthError:
        try:
            run_auth_flow()
        except AuthError as exc:
            raise SystemExit(str(exc)) from exc


def main() -> None:
    ensure_auth_ready()
    mcp.run()


if __name__ == "__main__":
    main()
