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


def _period_summary(period: str, now: str | None = None) -> dict[str, Any]:
    normalized = period.lower().strip()
    if normalized in {"week", "weekly", "last_7_days"}:
        return summarize_week(now=now)
    if normalized in {"month", "monthly", "this_month"}:
        return summarize_month(now=now)
    raise ValueError("period must be 'week' or 'month'")


def _breakdown_text(summary: dict[str, Any]) -> str:
    breakdown = summary.get("activity_type_breakdown") or {}
    if not breakdown:
        return "Belum ada aktivitas."
    return ", ".join(f"{kind}: {count}x" for kind, count in sorted(breakdown.items()))


def _report_title(period: str) -> str:
    return "Training report bulan ini" if period == "month" else "Training report minggu ini"


def _format_training_report(summary: dict[str, Any], period: str) -> str:
    longest = summary.get("longest_activity") or {}
    lines = [
        _report_title(period),
        f"Total: {summary['total_distance_km']} km",
        f"Durasi: {summary['total_moving_time']}",
        f"Elevasi: {summary['total_elevation_m']} m",
        f"Aktivitas: {summary['activity_count']}x",
        f"Breakdown: {_breakdown_text(summary)}",
    ]
    if longest:
        lines.append(
            "Terpanjang: "
            f"{longest.get('name')} — {longest.get('distance_km')} km, {longest.get('moving_time')}"
        )
    return "\n".join(lines)


def generate_training_report(period: str = "week", now: str | None = None) -> dict[str, Any]:
    """Generate Telegram-friendly training report text for week or month."""
    normalized = "month" if period.lower().strip() in {"month", "monthly", "this_month"} else "week"
    summary = _period_summary(normalized, now=now)
    text = _format_training_report(summary, normalized)
    return {"period": normalized, "summary": summary, "text": text}


def _stream_data(streams: Any, key: str) -> list[Any]:
    if isinstance(streams, dict):
        raw = streams.get(key)
        if isinstance(raw, dict):
            data = raw.get("data")
            return data if isinstance(data, list) else []
        return raw if isinstance(raw, list) else []
    if isinstance(streams, list):
        for stream in streams:
            if isinstance(stream, dict) and stream.get("type") == key:
                data = stream.get("data")
                return data if isinstance(data, list) else []
    return []


def _split_pace(distance_delta_m: float, time_delta_s: float) -> str | None:
    if distance_delta_m <= 0 or time_delta_s <= 0:
        return None
    return _pace_per_km(distance_delta_m, time_delta_s)


def _build_splits(
    distances: list[Any],
    times: list[Any],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    splits: list[dict[str, Any]] = []
    if len(distances) < 2 or len(times) < 2:
        return splits, None

    target = 1000.0
    prev_distance = 0.0
    prev_time = 0.0
    last_distance = float(distances[-1] or 0)
    last_time = float(times[-1] or 0)

    for distance, timestamp in zip(distances, times, strict=False):
        distance_f = float(distance or 0)
        time_f = float(timestamp or 0)
        if distance_f >= target:
            duration = time_f - prev_time
            splits.append(
                {
                    "km": len(splits) + 1,
                    "pace_per_km": _split_pace(1000, duration),
                    "duration": _human_duration(duration),
                }
            )
            prev_distance = target
            prev_time = time_f
            target += 1000

    remaining_distance = last_distance - prev_distance
    remaining_time = last_time - prev_time
    partial = None
    if remaining_distance > 0 and remaining_distance < 1000 and remaining_time > 0:
        partial = {
            "distance_km": round(remaining_distance / 1000, 2),
            "pace_per_km": _split_pace(remaining_distance, remaining_time),
            "duration": _human_duration(remaining_time),
        }
    return splits, partial


def _pace_trend(splits: list[dict[str, Any]]) -> str:
    if len(splits) < 2:
        return "not_enough_data"

    def split_seconds(value: str) -> int:
        pace = value.replace("/km", "")
        minutes, seconds = pace.split(":", 1)
        return int(minutes) * 60 + int(seconds)

    first = split_seconds(str(splits[0]["pace_per_km"]))
    last = split_seconds(str(splits[-1]["pace_per_km"]))
    if last < first:
        return "faster_finish"
    if last > first:
        return "slower_finish"
    return "steady"


def _format_run_analysis(activity: dict[str, Any], splits: list[dict[str, Any]]) -> str:
    formatted = _format_activity(activity)
    lines = [
        f"Analisis lari: {formatted.get('name')}",
        f"Jarak: {formatted.get('distance_km')} km",
        f"Durasi: {formatted.get('moving_time')}",
        f"Pace avg: {formatted.get('pace_per_km')}",
    ]
    for split in splits:
        lines.append(f"Km {split['km']}: {split['pace_per_km']}")
    return "\n".join(lines)


def analyze_run_activity(activity_id: int | None = None) -> dict[str, Any]:
    """Analyze a run activity with per-kilometer splits and pace trend."""
    if activity_id is None:
        activities = list_activities(per_page=1, page=1)
        if not activities:
            return {"activity": None, "splits": [], "text": "No recent run activity found."}
        activity_id = int(activities[0]["id"])

    activity = get_activity(activity_id)
    streams = get_activity_streams(activity_id, keys=["distance", "time", "heartrate"])
    splits, partial = _build_splits(
        _stream_data(streams, "distance"),
        _stream_data(streams, "time"),
    )
    return {
        "activity": _format_activity(activity),
        "splits": splits,
        "partial_split": partial,
        "pace_trend": _pace_trend(splits),
        "average_heartrate": activity.get("average_heartrate"),
        "text": _format_run_analysis(activity, splits),
    }


def generate_x_post(period: str = "week", now: str | None = None) -> dict[str, Any]:
    """Generate a copy-paste-ready X post from week or month training data."""
    normalized = "month" if period.lower().strip() in {"month", "monthly", "this_month"} else "week"
    report = generate_training_report(period=normalized, now=now)
    summary = report["summary"]
    period_text = "Bulan ini" if normalized == "month" else "Minggu ini"
    text = (
        f"{period_text} di Strava: {summary['activity_count']} aktivitas, "
        f"{summary['total_distance_km']} km, {summary['total_moving_time']}, "
        f"elevasi {summary['total_elevation_m']} m.\n\n"
        "Dibaca via strava-mcp, jadi data training bisa langsung masuk ke agent.\n"
        "https://github.com/audreyaaf/strava-mcp"
    )
    return {"text": text, "character_count": len(text), "fits_x": len(text) <= 280}
