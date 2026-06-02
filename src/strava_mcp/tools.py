from __future__ import annotations

from collections import defaultdict
from typing import Any

from .client import StravaClient, iso_to_epoch


def get_athlete() -> dict[str, Any]:
    """Get authenticated Strava athlete profile."""
    return StravaClient().get_athlete()


def list_activities(
    per_page: int = 10,
    page: int = 1,
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, Any]]:
    """List recent Strava activities. after/before accept ISO datetime strings."""
    return StravaClient().list_activities(
        per_page=per_page,
        page=page,
        after=iso_to_epoch(after),
        before=iso_to_epoch(before),
    )


def get_activity(activity_id: int, include_all_efforts: bool = False) -> dict[str, Any]:
    """Get detailed Strava activity by ID."""
    return StravaClient().get_activity(activity_id, include_all_efforts=include_all_efforts)


def get_activity_streams(activity_id: int, keys: list[str] | None = None) -> Any:
    """Get activity stream data like time, distance, GPS, HR, cadence, power."""
    return StravaClient().get_activity_streams(activity_id, keys=keys)


def _empty_type_totals() -> dict[str, float]:
    return {"distance_km": 0.0, "moving_time_hours": 0.0, "elevation_m": 0.0}


def summarize_training(
    per_page: int = 20,
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    """Summarize recent Strava activities."""
    activities = list_activities(per_page=per_page, after=after, before=before)
    by_type: dict[str, int] = defaultdict(int)
    totals_by_type: dict[str, dict[str, float]] = defaultdict(_empty_type_totals)

    total_distance_m = 0.0
    total_time_s = 0.0
    total_elevation_m = 0.0

    for activity in activities:
        kind = activity.get("type") or activity.get("sport_type") or "Unknown"
        distance_m = float(activity.get("distance") or 0)
        moving_time_s = float(activity.get("moving_time") or 0)
        elevation_m = float(activity.get("total_elevation_gain") or 0)

        by_type[kind] += 1
        total_distance_m += distance_m
        total_time_s += moving_time_s
        total_elevation_m += elevation_m
        totals_by_type[kind]["distance_km"] += distance_m / 1000
        totals_by_type[kind]["moving_time_hours"] += moving_time_s / 3600
        totals_by_type[kind]["elevation_m"] += elevation_m

    return {
        "activity_count": len(activities),
        "total_distance_km": round(total_distance_m / 1000, 2),
        "total_moving_time_hours": round(total_time_s / 3600, 2),
        "total_elevation_m": round(total_elevation_m, 1),
        "activity_type_breakdown": dict(by_type),
        "totals_by_type": {
            key: {metric: round(value, 2) for metric, value in totals.items()}
            for key, totals in totals_by_type.items()
        },
    }
