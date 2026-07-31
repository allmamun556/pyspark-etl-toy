"""
HTTP API extract: Open-Meteo (https://open-meteo.com), a free weather API
that requires no key/signup. Pulls the current observation for a fixed
location (a real North Sea wind-energy hub) so the pipeline has genuine
ambient weather to correlate against turbine output - not something a real
wind-farm operator would simulate, since it comes from an external provider
they don't control.

Fetching (HTTP + JSON parsing) is kept separate from parsing so unit tests
can exercise `parse_current_weather` against a fixed JSON fixture without
making a real network call.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from src.config import get_settings


@dataclass
class WeatherReading:
    source: str
    latitude: float
    longitude: float
    ts: datetime
    wind_speed_ms: float | None
    wind_direction_deg: float | None
    temperature_c: float | None
    pressure_hpa: float | None


def fetch_current_weather_raw() -> dict:
    """Real HTTP GET against the Open-Meteo API. No API key required."""
    settings = get_settings()
    response = requests.get(
        settings.weather_api_base_url,
        params={
            "latitude": settings.weather_latitude,
            "longitude": settings.weather_longitude,
            "current": "wind_speed_10m,wind_direction_10m,temperature_2m,surface_pressure",
            "wind_speed_unit": "ms",
            "timezone": "UTC",
        },
        timeout=settings.http_request_timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


def parse_current_weather(payload: dict) -> WeatherReading:
    current = payload["current"]
    # Open-Meteo returns naive local time in the requested timezone; we
    # always request "UTC" above, so attach UTC explicitly rather than
    # trusting an implicit assumption baked into the parser.
    ts = datetime.fromisoformat(current["time"]).replace(tzinfo=timezone.utc)
    return WeatherReading(
        source="open-meteo",
        latitude=payload["latitude"],
        longitude=payload["longitude"],
        ts=ts,
        wind_speed_ms=current.get("wind_speed_10m"),
        wind_direction_deg=current.get("wind_direction_10m"),
        temperature_c=current.get("temperature_2m"),
        pressure_hpa=current.get("surface_pressure"),
    )


def fetch_current_weather() -> WeatherReading:
    return parse_current_weather(fetch_current_weather_raw())
