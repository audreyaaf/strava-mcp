from strava_mcp.client import iso_to_epoch
from strava_mcp.config import env_client_id, env_client_secret


def test_iso_to_epoch_accepts_zulu_time():
    assert iso_to_epoch("2026-01-01T00:00:00Z") == 1767225600


def test_iso_to_epoch_none_returns_none():
    assert iso_to_epoch(None) is None


def test_env_client_credentials_read_new_names(monkeypatch):
    monkeypatch.setenv("STRAVA_CLIENT_ID", "abc")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "def")

    assert env_client_id() == "abc"
    assert env_client_secret() == "def"


def test_env_client_credentials_trim_whitespace(monkeypatch):
    monkeypatch.setenv("STRAVA_CLIENT_ID", "  abc  ")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "  def  ")

    assert env_client_id() == "abc"
    assert env_client_secret() == "def"
