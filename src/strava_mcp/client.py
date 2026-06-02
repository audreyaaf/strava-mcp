from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from .auth import get_access_token
from .config import STRAVA_API_BASE


class StravaClient:
    def __init__(self) -> None:
        self.base_url = STRAVA_API_BASE

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {get_access_token()}"}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = httpx.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            params=params or {},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_athlete(self) -> dict[str, Any]:
        return self.get("/athlete")

    def list_activities(
        self,
        per_page: int = 10,
        page: int = 1,
        after: int | None = None,
        before: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"per_page": per_page, "page": page}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        return self.get("/athlete/activities", params=params)

    def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> dict[str, Any]:
        return self.get(
            f"/activities/{activity_id}",
            params={"include_all_efforts": str(include_all_efforts).lower()},
        )

    def get_activity_streams(
        self,
        activity_id: int,
        keys: list[str] | None = None,
        key_by_type: bool = True,
    ) -> Any:
        keys = keys or [
            "time",
            "distance",
            "latlng",
            "altitude",
            "velocity_smooth",
            "heartrate",
            "cadence",
            "watts",
            "temp",
            "moving",
            "grade_smooth",
        ]
        return self.get(
            f"/activities/{activity_id}/streams",
            params={"keys": ",".join(keys), "key_by_type": str(key_by_type).lower()},
        )


def iso_to_epoch(value: str | None) -> int | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp())
