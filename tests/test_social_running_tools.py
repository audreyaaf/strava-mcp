from strava_mcp import tools

RUN_ACTIVITY = {
    "id": 99,
    "name": "Progression Run",
    "type": "Run",
    "distance": 3200,
    "moving_time": 960,
    "total_elevation_gain": 25,
    "average_heartrate": 148,
    "start_date": "2026-06-03T00:00:00Z",
}

WEEK_ACTIVITIES = [
    RUN_ACTIVITY,
    {
        "id": 100,
        "name": "Long Ride",
        "type": "Ride",
        "distance": 30000,
        "moving_time": 5400,
        "total_elevation_gain": 220,
        "start_date": "2026-06-01T00:00:00Z",
    },
]

STREAMS = {
    "distance": {"data": [0, 1000, 2000, 3000, 3200]},
    "time": {"data": [0, 330, 640, 930, 960]},
    "heartrate": {"data": [130, 145, 150, 158, 160]},
}


def test_generate_training_report_returns_telegram_ready_text(monkeypatch):
    monkeypatch.setattr(tools, "list_activities", lambda **kwargs: WEEK_ACTIVITIES)

    report = tools.generate_training_report(period="week", now="2026-06-04T00:00:00Z")

    assert report["period"] == "week"
    assert report["summary"]["activity_count"] == 2
    assert "Training report minggu ini" in report["text"]
    assert "Total: 33.2 km" in report["text"]
    assert "Durasi: 1h 46m" in report["text"]
    assert "Terpanjang: Long Ride" in report["text"]
    assert "Run: 1x" in report["text"]


def test_analyze_run_activity_builds_km_splits_and_trend(monkeypatch):
    monkeypatch.setattr(tools, "list_activities", lambda **kwargs: [RUN_ACTIVITY])
    monkeypatch.setattr(tools, "get_activity", lambda activity_id: RUN_ACTIVITY)
    monkeypatch.setattr(tools, "get_activity_streams", lambda activity_id, keys=None: STREAMS)

    analysis = tools.analyze_run_activity()

    assert analysis["activity"]["id"] == 99
    assert analysis["splits"][0] == {"km": 1, "pace_per_km": "5:30/km", "duration": "5m 30s"}
    assert analysis["splits"][1]["pace_per_km"] == "5:10/km"
    assert analysis["partial_split"] == {
        "distance_km": 0.2,
        "pace_per_km": "2:30/km",
        "duration": "30s",
    }
    assert analysis["pace_trend"] == "faster_finish"
    assert analysis["average_heartrate"] == 148
    assert "Progression Run" in analysis["text"]
    assert "Km 1: 5:30/km" in analysis["text"]


def test_generate_x_post_is_copy_paste_ready_and_under_limit(monkeypatch):
    monkeypatch.setattr(tools, "list_activities", lambda **kwargs: WEEK_ACTIVITIES)

    post = tools.generate_x_post(period="week", now="2026-06-04T00:00:00Z")

    assert post["character_count"] <= 280
    assert post["fits_x"] is True
    assert "Minggu ini di Strava" in post["text"]
    assert "33.2 km" in post["text"]
    assert "1h 46m" in post["text"]
    assert "strava-mcp" in post["text"]
