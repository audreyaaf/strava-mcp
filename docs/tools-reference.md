# MCP Tools Reference

## `get_athlete`

Get the authenticated Strava athlete profile.

Input: none

Returns: Strava athlete profile JSON.

## `list_activities`

List recent activities.

Input:

- `per_page` integer, default `10`
- `page` integer, default `1`
- `after` optional ISO datetime string, e.g. `2026-01-01T00:00:00Z`
- `before` optional ISO datetime string

Returns: list of Strava activity summaries.

## `get_activity`

Get detailed activity data by ID.

Input:

- `activity_id` integer
- `include_all_efforts` boolean, default `false`

Returns: Strava activity detail JSON.

## `get_activity_streams`

Get activity streams such as time, distance, GPS, altitude, heart rate, cadence, power, temperature, moving status, and grade.

Input:

- `activity_id` integer
- `keys` optional list of stream keys

Default keys:

- `time`
- `distance`
- `latlng`
- `altitude`
- `velocity_smooth`
- `heartrate`
- `cadence`
- `watts`
- `temp`
- `moving`
- `grade_smooth`

Returns: Strava streams response.

## `summarize_training`

Summarize recent activity totals.

Input:

- `per_page` integer, default `20`
- `after` optional ISO datetime string
- `before` optional ISO datetime string

Returns:

- `activity_count`
- `total_distance_km`
- `total_moving_time_hours`
- `total_elevation_m`
- `activity_type_breakdown`
- `totals_by_type`
