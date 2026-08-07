"""
Validation layer for the solar plant fleet. Same six-dimension shape as
validators.py (validity, consistency-via-transform, timeliness, uniqueness,
completeness, schema) - kept as a parallel file rather than folded into
validators.py since it's typed against TransformedSolarReading, not
TransformedReading, and the two sources shouldn't need to know about each
other's dataclass.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.config import get_settings
from src.transform.solar_transformers import TransformedSolarReading

SOLAR_VALID_STATUS_CODES = {"operational", "night", "curtailed", "fault", "maintenance", "offline"}


@dataclass
class SolarValidationResult:
    reading: TransformedSolarReading
    is_valid: bool
    reasons: list[str]


def validate_solar_reading(reading: TransformedSolarReading) -> SolarValidationResult:
    settings = get_settings()
    reasons: list[str] = []

    if not (0 <= reading.irradiance_w_m2 <= settings.max_irradiance_w_m2):
        reasons.append(
            f"irradiance_w_m2 {reading.irradiance_w_m2} outside [0, {settings.max_irradiance_w_m2}]"
        )

    if not (settings.min_panel_temp_c <= reading.panel_temp_c <= settings.max_panel_temp_c):
        reasons.append(
            f"panel_temp_c {reading.panel_temp_c} outside "
            f"[{settings.min_panel_temp_c}, {settings.max_panel_temp_c}]"
        )

    if not (0 <= reading.dc_power_kw <= settings.max_dc_power_kw):
        reasons.append(f"dc_power_kw {reading.dc_power_kw} outside [0, {settings.max_dc_power_kw}]")

    if not (0 <= reading.ac_power_kw <= settings.max_ac_power_kw):
        reasons.append(f"ac_power_kw {reading.ac_power_kw} outside [0, {settings.max_ac_power_kw}]")

    if reading.ac_power_kw > reading.dc_power_kw + 0.5:
        reasons.append(
            f"ac_power_kw {reading.ac_power_kw} exceeds dc_power_kw {reading.dc_power_kw} "
            "- inverter cannot output more than it receives"
        )

    if not (0 <= reading.inverter_efficiency_pct <= 100):
        reasons.append(
            f"inverter_efficiency_pct {reading.inverter_efficiency_pct} outside [0, 100]"
        )

    if reading.status_code not in SOLAR_VALID_STATUS_CODES:
        reasons.append(f"unrecognized status_code '{reading.status_code}'")

    if not reading.plant_id:
        reasons.append("missing plant_id")

    if reading.ts is None:
        reasons.append("missing ts")
    else:
        skew = timedelta(seconds=settings.max_future_skew_seconds)
        now = datetime.now(timezone.utc)
        if reading.ts > now + skew:
            reasons.append(
                f"ts {reading.ts.isoformat()} is more than {settings.max_future_skew_seconds}s "
                f"in the future (now={now.isoformat()}) - likely a bad sensor clock"
            )

    return SolarValidationResult(reading=reading, is_valid=not reasons, reasons=reasons)


def find_solar_batch_duplicates(
    readings: list[TransformedSolarReading],
) -> set[tuple[str, datetime]]:
    """(plant_id, ts) keys appearing more than once within a single batch."""
    seen: set[tuple[str, datetime]] = set()
    dupes: set[tuple[str, datetime]] = set()
    for r in readings:
        key = (r.plant_id, r.ts)
        if key in seen:
            dupes.add(key)
        seen.add(key)
    return dupes


def validate_solar_batch(
    readings: list[TransformedSolarReading],
) -> tuple[list[TransformedSolarReading], list[SolarValidationResult]]:
    """Returns (valid_readings, failed_results)."""
    valid: list[TransformedSolarReading] = []
    failed: list[SolarValidationResult] = []

    duplicate_keys = find_solar_batch_duplicates(readings)
    first_occurrence_seen: set[tuple[str, datetime]] = set()

    for reading in readings:
        result = validate_solar_reading(reading)
        key = (reading.plant_id, reading.ts)

        if key in duplicate_keys:
            if key in first_occurrence_seen:
                result = SolarValidationResult(
                    reading=reading,
                    is_valid=False,
                    reasons=result.reasons + [f"duplicate plant_id+ts within batch: {key}"],
                )
            else:
                first_occurrence_seen.add(key)

        if result.is_valid:
            valid.append(reading)
        else:
            failed.append(result)

    return valid, failed


def expected_solar_batch_row_count(
    window_start: datetime, window_end: datetime, plant_count: int, interval_seconds: int
) -> int:
    """Deterministic expected row count, mirrors expected_batch_row_count for wind."""
    ticks = 0
    ts = window_start
    step = timedelta(seconds=interval_seconds)
    while ts < window_end:
        ticks += 1
        ts += step
    return ticks * plant_count


def check_solar_batch_completeness(
    actual_row_count: int, window_start: datetime, window_end: datetime
) -> list[str]:
    settings = get_settings()
    expected = expected_solar_batch_row_count(
        window_start, window_end, settings.solar_plant_count, settings.reading_interval_seconds
    )
    if expected and actual_row_count < expected:
        missing_pct = 100 * (expected - actual_row_count) / expected
        return [
            f"completeness check: expected {expected} rows for window "
            f"[{window_start.isoformat()}, {window_end.isoformat()}), got {actual_row_count} "
            f"({missing_pct:.1f}% missing)"
        ]
    return []
