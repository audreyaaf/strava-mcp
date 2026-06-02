from strava_mcp import tools


def test_summarize_training(monkeypatch):
    monkeypatch.setattr(
        tools,
        "list_activities",
        lambda per_page=20, after=None, before=None, page=1: [
            {"type": "Run", "distance": 5000, "moving_time": 1500, "total_elevation_gain": 20},
            {"type": "Ride", "distance": 20000, "moving_time": 3600, "total_elevation_gain": 120},
        ],
    )

    summary = tools.summarize_training(per_page=2)

    assert summary["activity_count"] == 2
    assert summary["total_distance_km"] == 25
    assert summary["total_moving_time_hours"] == 1.42
    assert summary["activity_type_breakdown"] == {"Run": 1, "Ride": 1}
