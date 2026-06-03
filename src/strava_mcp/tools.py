from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
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


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat()


def _seconds(value: Any) -> int:
    return int(float(value or 0))


def _meters(value: Any) -> float:
    return float(value or 0)


def _human_duration(seconds: Any) -> str:
    total = _seconds(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m" if secs == 0 else f"{minutes}m {secs}s"
    return f"{secs}s"


def _pace_per_km(distance_m: Any, moving_time_s: Any) -> str | None:
    distance = _meters(distance_m)
    seconds = _seconds(moving_time_s)
    if distance <= 0 or seconds <= 0:
        return None
    pace_seconds = int(round(seconds / (distance / 1000)))
    minutes, secs = divmod(pace_seconds, 60)
    return f"{minutes}:{secs:02d}/km"


def _speed_kmh(distance_m: Any, moving_time_s: Any) -> float | None:
    distance = _meters(distance_m)
    seconds = _seconds(moving_time_s)
    if distance <= 0 or seconds <= 0:
        return None
    return round((distance / 1000) / (seconds / 3600), 2)


def _activity_type(activity: dict[str, Any]) -> str:
    return str(activity.get("type") or activity.get("sport_type") or "Unknown")


def _format_activity(activity: dict[str, Any]) -> dict[str, Any]:
    distance_m = _meters(activity.get("distance"))
    moving_time_s = _seconds(activity.get("moving_time"))
    kind = _activity_type(activity)
    formatted = {
        "id": activity.get("id"),
        "name": activity.get("name"),
        "type": kind,
        "start_date": activity.get("start_date"),
        "distance_km": round(distance_m / 1000, 2),
        "moving_time": _human_duration(moving_time_s),
        "moving_time_seconds": moving_time_s,
        "elevation_m": round(_meters(activity.get("total_elevation_gain")), 1),
    }
    if kind.lower() == "run":
        formatted["pace_per_km"] = _pace_per_km(distance_m, moving_time_s)
    else:
        formatted["speed_kmh"] = _speed_kmh(distance_m, moving_time_s)
    if activity.get("average_heartrate") is not None:
        formatted["average_heartrate"] = activity.get("average_heartrate")
    return formatted


def _summarize_activities(
    activities: list[dict[str, Any]],
    period: str | None = None,
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    by_type: dict[str, int] = defaultdict(int)
    totals_by_type: dict[str, dict[str, float]] = defaultdict(_empty_type_totals)

    total_distance_m = 0.0
    total_time_s = 0.0
    total_elevation_m = 0.0

    for activity in activities:
        kind = _activity_type(activity)
        distance_m = _meters(activity.get("distance"))
        moving_time_s = _seconds(activity.get("moving_time"))
        elevation_m = _meters(activity.get("total_elevation_gain"))

        by_type[kind] += 1
        total_distance_m += distance_m
        total_time_s += moving_time_s
        total_elevation_m += elevation_m
        totals_by_type[kind]["distance_km"] += distance_m / 1000
        totals_by_type[kind]["moving_time_hours"] += moving_time_s / 3600
        totals_by_type[kind]["elevation_m"] += elevation_m

    longest = max(activities, key=lambda item: _meters(item.get("distance")), default=None)
    summary: dict[str, Any] = {
        "activity_count": len(activities),
        "total_distance_km": round(total_distance_m / 1000, 2),
        "total_moving_time_hours": round(total_time_s / 3600, 2),
        "total_moving_time": _human_duration(total_time_s),
        "total_elevation_m": round(total_elevation_m, 1),
        "activity_type_breakdown": dict(by_type),
        "totals_by_type": {
            key: {metric: round(value, 2) for metric, value in totals.items()}
            for key, totals in totals_by_type.items()
        },
    }
    if period:
        summary["period"] = period
    if after:
        summary["after"] = after
    if before:
        summary["before"] = before
    if longest:
        summary["longest_activity"] = _format_activity(longest)
    return summary


def summarize_training(
    per_page: int = 20,
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    """Summarize recent Strava activities."""
    activities = list_activities(per_page=per_page, after=after, before=before)
    return _summarize_activities(activities, after=after, before=before)


def get_recent_activity() -> dict[str, Any]:
    """Get the most recent Strava activity with human-friendly metrics."""
    activities = list_activities(per_page=1, page=1)
    if not activities:
        return {"activity": None, "message": "No recent activities found."}
    return _format_activity(activities[0])


def summarize_week(now: str | None = None) -> dict[str, Any]:
    """Summarize activities from the last 7 days."""
    end = _parse_dt(now)
    start = end - timedelta(days=7)
    after = _iso(start)
    before = _iso(end)
    activities = list_activities(per_page=100, after=after, before=before)
    return _summarize_activities(activities, period="last_7_days", after=after, before=before)


def summarize_month(now: str | None = None) -> dict[str, Any]:
    """Summarize activities from the current calendar month."""
    end = _parse_dt(now)
    start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    after = _iso(start)
    before = _iso(end)
    activities = list_activities(per_page=200, after=after, before=before)
    return _summarize_activities(activities, period="this_month", after=after, before=before)


def compare_weeks(now: str | None = None) -> dict[str, Any]:
    """Compare the last 7 days against the previous 7 days."""
    current_end = _parse_dt(now)
    current_start = current_end - timedelta(days=7)
    previous_start = current_start - timedelta(days=7)

    current_after = _iso(current_start)
    current_before = _iso(current_end)
    previous_after = _iso(previous_start)
    previous_before = _iso(current_start)

    current = _summarize_activities(
        list_activities(per_page=100, after=current_after, before=current_before),
        period="current_7_days",
        after=current_after,
        before=current_before,
    )
    previous = _summarize_activities(
        list_activities(per_page=100, after=previous_after, before=previous_before),
        period="previous_7_days",
        after=previous_after,
        before=previous_before,
    )

    return {
        "current_week": current,
        "previous_week": previous,
        "delta": {
            "activity_count": current["activity_count"] - previous["activity_count"],
            "distance_km": round(
                current["total_distance_km"] - previous["total_distance_km"], 2
            ),
            "moving_time_hours": round(
                current["total_moving_time_hours"] - previous["total_moving_time_hours"], 2
            ),
            "elevation_m": round(current["total_elevation_m"] - previous["total_elevation_m"], 1),
        },
    }


def _record(activities: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    if not activities:
        return None
    return _format_activity(max(activities, key=lambda item: _meters(item.get(key))))


def find_personal_bests(per_page: int = 200) -> dict[str, Any]:
    """Find simple personal bests from recent Strava activities."""
    activities = list_activities(per_page=per_page)
    runs = [activity for activity in activities if _activity_type(activity).lower() == "run"]
    rides = [activity for activity in activities if _activity_type(activity).lower() == "ride"]

    return {
        "activity_count_scanned": len(activities),
        "longest_activity": _record(activities, "distance"),
        "longest_run": _record(runs, "distance"),
        "longest_ride": _record(rides, "distance"),
        "most_elevation": _record(activities, "total_elevation_gain"),
        "longest_moving_time": _record(activities, "moving_time"),
    }
