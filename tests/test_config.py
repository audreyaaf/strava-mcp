from strava_mcp.client import iso_to_epoch


def test_iso_to_epoch_accepts_zulu_time():
    assert iso_to_epoch("2026-01-01T00:00:00Z") == 1767225600


def test_iso_to_epoch_none_returns_none():
    assert iso_to_epoch(None) is None
