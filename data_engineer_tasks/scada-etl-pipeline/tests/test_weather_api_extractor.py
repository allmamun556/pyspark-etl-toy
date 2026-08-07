from datetime import datetime, timezone

from src.extract.weather_api_extractor import parse_current_weather
from src.validation.external_validators import validate_weather_reading

# Fixed fixture shaped exactly like a real Open-Meteo response, so these
# tests never touch the network.
SAMPLE_PAYLOAD = {
    "latitude": 53.54,
    "longitude": 8.1,
    "current": {
        "time": "2026-07-31T12:15",
        "interval": 900,
        "wind_speed_10m": 3.61,
        "wind_direction_10m": 326,
        "temperature_2m": 21.2,
        "surface_pressure": 1014.0,
        "shortwave_radiation": 446.0,
    },
}


def test_parse_current_weather_maps_fields():
    reading = parse_current_weather(SAMPLE_PAYLOAD)
    assert reading.source == "open-meteo"
    assert reading.latitude == 53.54
    assert reading.longitude == 8.1
    assert reading.wind_speed_ms == 3.61
    assert reading.wind_direction_deg == 326
    assert reading.temperature_c == 21.2
    assert reading.pressure_hpa == 1014.0
    assert reading.shortwave_radiation_w_m2 == 446.0


def test_parse_current_weather_ts_is_utc_aware():
    reading = parse_current_weather(SAMPLE_PAYLOAD)
    assert reading.ts == datetime(2026, 7, 31, 12, 15, tzinfo=timezone.utc)


def test_valid_weather_reading_passes():
    reading = parse_current_weather(SAMPLE_PAYLOAD)
    result = validate_weather_reading(reading)
    assert result.is_valid
    assert result.reasons == []


def test_missing_wind_speed_fails():
    payload = {**SAMPLE_PAYLOAD, "current": {**SAMPLE_PAYLOAD["current"], "wind_speed_10m": None}}
    reading = parse_current_weather(payload)
    result = validate_weather_reading(reading)
    assert not result.is_valid
    assert any("wind_speed_ms" in r for r in result.reasons)


def test_out_of_range_temperature_fails():
    payload = {**SAMPLE_PAYLOAD, "current": {**SAMPLE_PAYLOAD["current"], "temperature_2m": 500}}
    reading = parse_current_weather(payload)
    result = validate_weather_reading(reading)
    assert not result.is_valid
    assert any("temperature_c" in r for r in result.reasons)


def test_out_of_range_shortwave_radiation_fails():
    payload = {
        **SAMPLE_PAYLOAD,
        "current": {**SAMPLE_PAYLOAD["current"], "shortwave_radiation": 5000},
    }
    reading = parse_current_weather(payload)
    result = validate_weather_reading(reading)
    assert not result.is_valid
    assert any("shortwave_radiation_w_m2" in r for r in result.reasons)
