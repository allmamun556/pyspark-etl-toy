"""
Lightweight validation for the external (weather API / IoT buoy) sources.

Unlike src/validation/validators.py, these sources deliver one reading per
fetch rather than a batch of hundreds, so there's no batch-level duplicate
or completeness check here - just physical-plausibility bounds, same
"reject with a reason, don't silently drop" philosophy as the main pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.extract.iot_buoy_extractor import BuoyReading
from src.extract.weather_api_extractor import WeatherReading


@dataclass
class ExternalValidationResult:
    is_valid: bool
    reasons: list[str]


def validate_weather_reading(reading: WeatherReading) -> ExternalValidationResult:
    reasons: list[str] = []

    if reading.wind_speed_ms is None:
        reasons.append("wind_speed_ms is missing")
    elif not (0 <= reading.wind_speed_ms <= 100):
        reasons.append(f"wind_speed_ms {reading.wind_speed_ms} outside [0, 100]")

    if reading.temperature_c is not None and not (-90 <= reading.temperature_c <= 60):
        reasons.append(f"temperature_c {reading.temperature_c} outside [-90, 60]")

    if reading.pressure_hpa is not None and not (800 <= reading.pressure_hpa <= 1100):
        reasons.append(f"pressure_hpa {reading.pressure_hpa} outside [800, 1100]")

    if reading.shortwave_radiation_w_m2 is not None and not (
        0 <= reading.shortwave_radiation_w_m2 <= 1400
    ):
        reasons.append(
            f"shortwave_radiation_w_m2 {reading.shortwave_radiation_w_m2} outside [0, 1400]"
        )

    return ExternalValidationResult(is_valid=not reasons, reasons=reasons)


def validate_buoy_reading(reading: BuoyReading) -> ExternalValidationResult:
    reasons: list[str] = []

    if reading.wind_speed_ms is None:
        reasons.append("wind_speed_ms is missing")
    elif not (0 <= reading.wind_speed_ms <= 100):
        reasons.append(f"wind_speed_ms {reading.wind_speed_ms} outside [0, 100]")

    if reading.wave_height_m is not None and not (0 <= reading.wave_height_m <= 30):
        reasons.append(f"wave_height_m {reading.wave_height_m} outside [0, 30]")

    if reading.air_temp_c is not None and not (-60 <= reading.air_temp_c <= 60):
        reasons.append(f"air_temp_c {reading.air_temp_c} outside [-60, 60]")

    if reading.pressure_hpa is not None and not (800 <= reading.pressure_hpa <= 1100):
        reasons.append(f"pressure_hpa {reading.pressure_hpa} outside [800, 1100]")

    return ExternalValidationResult(is_valid=not reasons, reasons=reasons)
