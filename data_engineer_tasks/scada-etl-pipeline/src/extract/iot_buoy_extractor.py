"""
IoT extract: NOAA National Data Buoy Center (NDBC) real-time feed
(https://www.ndbc.noaa.gov/data/realtime2/<station>.txt). These are genuine
moored ocean buoys - real IoT hardware transmitting live sensor telemetry
(wind, waves, pressure, temperature) via satellite - not a simulation, and
free with no API key.

The feed is a fixed-width whitespace-delimited text file, newest reading
first, with "MM" marking a missing sensor value. As with the weather
extractor, fetching is separate from parsing so tests can exercise
`parse_realtime2` against a fixed text fixture with no network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from src.config import get_settings

# Column order in NDBC's realtime2 format, after the two '#'-prefixed header
# lines: YY MM DD hh mm WDIR WSPD GST WVHT DPD APD MWD PRES ATMP WTMP DEWP VIS PTDY TIDE
_MISSING = "MM"


@dataclass
class BuoyReading:
    station_id: str
    ts: datetime
    wind_speed_ms: float | None
    wind_gust_ms: float | None
    wave_height_m: float | None
    air_temp_c: float | None
    water_temp_c: float | None
    pressure_hpa: float | None


def _parse_field(value: str) -> float | None:
    return None if value == _MISSING else float(value)


def fetch_realtime_buoy_text(station_id: str | None = None) -> str:
    """Real HTTP GET against NOAA NDBC. No API key required."""
    settings = get_settings()
    station_id = station_id or settings.iot_buoy_station_id
    response = requests.get(
        f"{settings.iot_buoy_base_url}/{station_id}.txt",
        timeout=settings.http_request_timeout_seconds,
    )
    response.raise_for_status()
    return response.text


def parse_realtime2(text: str, station_id: str) -> BuoyReading:
    """Parses the newest (first) data row - lines 0/1 are '#'-prefixed headers."""
    lines = [line for line in text.splitlines() if line.strip()]
    data_lines = [line for line in lines if not line.startswith("#")]
    if not data_lines:
        raise ValueError(f"no data rows in NDBC realtime2 feed for station {station_id}")

    fields = data_lines[0].split()
    year, month, day, hour, minute = (int(f) for f in fields[0:5])
    ts = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

    return BuoyReading(
        station_id=station_id,
        ts=ts,
        wind_speed_ms=_parse_field(fields[6]),
        wind_gust_ms=_parse_field(fields[7]),
        wave_height_m=_parse_field(fields[8]),
        pressure_hpa=_parse_field(fields[12]),
        air_temp_c=_parse_field(fields[13]),
        water_temp_c=_parse_field(fields[14]),
    )


def fetch_latest_buoy_reading(station_id: str | None = None) -> BuoyReading:
    settings = get_settings()
    station_id = station_id or settings.iot_buoy_station_id
    return parse_realtime2(fetch_realtime_buoy_text(station_id), station_id)
