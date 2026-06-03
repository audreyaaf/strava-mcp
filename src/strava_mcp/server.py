from __future__ import annotations

import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import tools
from .auth import AuthError, load_token, print_setup_guide

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


@mcp.tool()
def get_recent_activity() -> dict[str, Any]:
    """Get the latest Strava activity with formatted pace/speed and duration."""
    return tools.get_recent_activity()


@mcp.tool()
def summarize_week(now: str | None = None) -> dict[str, Any]:
    """Summarize the last 7 days of training."""
    return tools.summarize_week(now=now)


@mcp.tool()
def summarize_month(now: str | None = None) -> dict[str, Any]:
    """Summarize the current calendar month of training."""
    return tools.summarize_month(now=now)


@mcp.tool()
def compare_weeks(now: str | None = None) -> dict[str, Any]:
    """Compare the last 7 days versus the previous 7 days."""
    return tools.compare_weeks(now=now)


@mcp.tool()
def find_personal_bests(per_page: int = 200) -> dict[str, Any]:
    """Find simple personal bests like longest activity, run, ride, and elevation."""
    return tools.find_personal_bests(per_page=per_page)


@mcp.tool()
def generate_training_report(period: str = "week", now: str | None = None) -> dict[str, Any]:
    """Generate Telegram-friendly weekly or monthly training report text."""
    return tools.generate_training_report(period=period, now=now)


@mcp.tool()
def analyze_run_activity(activity_id: int | None = None) -> dict[str, Any]:
    """Analyze a run with kilometer splits, pace trend, and formatted text."""
    return tools.analyze_run_activity(activity_id=activity_id)


@mcp.tool()
def generate_x_post(period: str = "week", now: str | None = None) -> dict[str, Any]:
    """Generate a copy-paste-ready X post from Strava training data."""
    return tools.generate_x_post(period=period, now=now)


def ensure_auth_ready() -> None:
    try:
        load_token()
    except AuthError:
        print_setup_guide()
        sys.exit(1)


def main() -> None:
    ensure_auth_ready()
    mcp.run()


if __name__ == "__main__":
    main()
