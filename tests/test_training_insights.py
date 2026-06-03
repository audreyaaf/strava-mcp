from strava_mcp import tools

SAMPLE_ACTIVITIES = [
    {
        "id": 1,
        "name": "Morning Run",
        "type": "Run",
        "distance": 5000,
        "moving_time": 1500,
        "elapsed_time": 1600,
        "total_elevation_gain": 20,
        "average_heartrate": 150,
        "start_date": "2026-06-03T00:00:00Z",
    },
    {
        "id": 2,
        "name": "Long Ride",
        "type": "Ride",
        "distance": 40000,
        "moving_time": 7200,
        "elapsed_time": 7500,
        "total_elevation_gain": 350,
        "average_speed": 5.56,
        "start_date": "2026-06-01T00:00:00Z",
    },
    {
        "id": 3,
        "name": "Easy Run",
        "type": "Run",
        "distance": 3000,
        "moving_time": 1080,
        "elapsed_time": 1100,
        "total_elevation_gain": 10,
        "start_date": "2026-05-28T00:00:00Z",
    },
]


def test_get_recent_activity_returns_human_friendly_activity(monkeypatch):
    monkeypatch.setattr(
        tools,
        "list_activities",
        lambda per_page=1, page=1, after=None, before=None: [SAMPLE_ACTIVITIES[0]],
    )

    recent = tools.get_recent_activity()

    assert recent["id"] == 1
    assert recent["name"] == "Morning Run"
    assert recent["distance_km"] == 5
    assert recent["moving_time"] == "25m"
    assert recent["pace_per_km"] == "5:00/km"
    assert recent["average_heartrate"] == 150


def test_summarize_week_uses_last_7_days_window(monkeypatch):
    calls = []

    def fake_list_activities(per_page=100, page=1, after=None, before=None):
        calls.append({"after": after, "before": before, "per_page": per_page})
        return SAMPLE_ACTIVITIES[:2]

    monkeypatch.setattr(tools, "list_activities", fake_list_activities)

    summary = tools.summarize_week(now="2026-06-04T00:00:00Z")

    assert summary["period"] == "last_7_days"
    assert summary["activity_count"] == 2
    assert summary["total_distance_km"] == 45
    assert summary["longest_activity"]["name"] == "Long Ride"
    assert calls[0]["after"] == "2026-05-28T00:00:00+00:00"
    assert calls[0]["before"] == "2026-06-04T00:00:00+00:00"


def test_summarize_month_uses_current_month_window(monkeypatch):
    calls = []

    def fake_list_activities(per_page=200, page=1, after=None, before=None):
        calls.append({"after": after, "before": before, "per_page": per_page})
        return SAMPLE_ACTIVITIES[:2]

    monkeypatch.setattr(tools, "list_activities", fake_list_activities)

    summary = tools.summarize_month(now="2026-06-15T12:00:00Z")

    assert summary["period"] == "this_month"
    assert summary["activity_count"] == 2
    assert summary["total_distance_km"] == 45
    assert calls[0]["after"] == "2026-06-01T00:00:00+00:00"
    assert calls[0]["before"] == "2026-06-15T12:00:00+00:00"


def test_compare_weeks_reports_delta(monkeypatch):
    calls = []

    def fake_list_activities(per_page=100, page=1, after=None, before=None):
        calls.append({"after": after, "before": before})
        if len(calls) == 1:
            return SAMPLE_ACTIVITIES[:2]
        return [SAMPLE_ACTIVITIES[2]]

    monkeypatch.setattr(tools, "list_activities", fake_list_activities)

    comparison = tools.compare_weeks(now="2026-06-04T00:00:00Z")

    assert comparison["current_week"]["activity_count"] == 2
    assert comparison["previous_week"]["activity_count"] == 1
    assert comparison["delta"]["distance_km"] == 42
    assert comparison["delta"]["activity_count"] == 1


def test_find_personal_bests_returns_distance_time_elevation_records(monkeypatch):
    monkeypatch.setattr(
        tools,
        "list_activities",
        lambda per_page=200, page=1, after=None, before=None: SAMPLE_ACTIVITIES,
    )

    records = tools.find_personal_bests()

    assert records["longest_activity"]["name"] == "Long Ride"
    assert records["longest_run"]["name"] == "Morning Run"
    assert records["longest_ride"]["name"] == "Long Ride"
    assert records["most_elevation"]["elevation_m"] == 350
    assert records["longest_moving_time"]["moving_time"] == "2h 0m"
