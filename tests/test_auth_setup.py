from strava_mcp.auth import get_missing_credentials, get_setup_guide


def test_get_missing_credentials_reports_both(monkeypatch):
    monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
    monkeypatch.delenv("STRAVA_CLIENT_SECRET", raising=False)

    assert get_missing_credentials() == ["STRAVA_CLIENT_ID", "STRAVA_CLIENT_SECRET"]


def test_setup_guide_contains_required_steps(monkeypatch):
    monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
    monkeypatch.delenv("STRAVA_CLIENT_SECRET", raising=False)

    guide = get_setup_guide()

    assert "https://www.strava.com/settings/api" in guide
    assert "Authorization Callback Domain" in guide
    assert "localhost" in guide
    assert "STRAVA_CLIENT_ID" in guide
    assert "STRAVA_CLIENT_SECRET" in guide
    assert "tidak memakai shared credentials" in guide
