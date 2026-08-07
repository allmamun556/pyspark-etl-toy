"""
Validation layer.

Every transformed reading is checked against physical bounds and business
rules *before* it reaches the load layer. Rows that fail are routed to a
reject sink with a human-readable reason instead of being silently dropped —
losing SCADA rows silently is exactly how availability/production reports
end up quietly wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.config import get_settings
from src.transform.transformers import TransformedReading

VALID_STATUS_CODES = {"operational", "curtailed", "fault", "maintenance", "offline"}


@dataclass
class ValidationResult:
    reading: TransformedReading
    is_valid: bool
    reasons: list[str]


def validate_reading(reading: TransformedReading) -> ValidationResult:
    settings = get_settings()
    reasons: list[str] = []

    if reading.wind_speed_ms < 0 or reading.wind_speed_ms > settings.max_wind_speed_ms:
        reasons.append(
            f"wind_speed_ms {reading.wind_speed_ms} outside [0, {settings.max_wind_speed_ms}]"
        )

    if reading.power_kw < 0 or reading.power_kw > settings.max_power_kw:
        reasons.append(f"power_kw {reading.power_kw} outside [0, {settings.max_power_kw}]")

    if reading.rotor_rpm < 0 or reading.rotor_rpm > settings.max_rotor_rpm:
        reasons.append(f"rotor_rpm {reading.rotor_rpm} outside [0, {settings.max_rotor_rpm}]")

    if not (settings.min_nacelle_temp_c <= reading.nacelle_temp_c <= settings.max_nacelle_temp_c):
        reasons.append(
            f"nacelle_temp_c {reading.nacelle_temp_c} outside "
            f"[{settings.min_nacelle_temp_c}, {settings.max_nacelle_temp_c}]"
        )

    if not (0 <= reading.pitch_angle_deg <= 90):
        reasons.append(f"pitch_angle_deg {reading.pitch_angle_deg} outside [0, 90]")

    if reading.status_code not in VALID_STATUS_CODES:
        reasons.append(f"unrecognized status_code '{reading.status_code}'")

    if not reading.turbine_id:
        reasons.append("missing turbine_id")

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

    return ValidationResult(reading=reading, is_valid=not reasons, reasons=reasons)


def find_batch_duplicates(readings: list[TransformedReading]) -> set[tuple[str, datetime]]:
    """
    (turbine_id, ts) keys that appear more than once within a single batch.
    This is the uniqueness dimension checked pre-load: the DB's unique
    constraint on (turbine_id, ts) already makes loads idempotent across
    runs, but it can't tell us *within* one extract that a comms glitch
    double-sent a reading - that's worth surfacing as a reject, not a
    silent UPSERT overwrite.
    """
    seen: set[tuple[str, datetime]] = set()
    dupes: set[tuple[str, datetime]] = set()
    for r in readings:
        key = (r.turbine_id, r.ts)
        if key in seen:
            dupes.add(key)
        seen.add(key)
    return dupes


def validate_batch(
    readings: list[TransformedReading],
) -> tuple[list[TransformedReading], list[ValidationResult]]:
    """Returns (valid_readings, failed_results)."""
    valid: list[TransformedReading] = []
    failed: list[ValidationResult] = []

    duplicate_keys = find_batch_duplicates(readings)
    first_occurrence_seen: set[tuple[str, datetime]] = set()

    for reading in readings:
        result = validate_reading(reading)
        key = (reading.turbine_id, reading.ts)

        if key in duplicate_keys:
            if key in first_occurrence_seen:
                result = ValidationResult(
                    reading=reading,
                    is_valid=False,
                    reasons=result.reasons + [f"duplicate turbine_id+ts within batch: {key}"],
                )
            else:
                first_occurrence_seen.add(key)

        if result.is_valid:
            valid.append(reading)
        else:
            failed.append(result)

    return valid, failed


def expected_batch_row_count(
    window_start: datetime, window_end: datetime, turbine_count: int, interval_seconds: int
) -> int:
    """
    Deterministic row count a batch *should* have for a given extraction
    window - mirrors the tick loop in ScadaSimulator.extract exactly, so
    completeness can be checked without any tolerance/fuzz.
    """
    ticks = 0
    ts = window_start
    step = timedelta(seconds=interval_seconds)
    while ts < window_end:
        ticks += 1
        ts += step
    return ticks * turbine_count


def check_batch_completeness(
    actual_row_count: int, window_start: datetime, window_end: datetime
) -> list[str]:
    """
    Batch-level completeness check: did extraction return as many rows as
    the window/turbine-count/interval imply it should have? A shortfall
    here means rows went missing somewhere upstream of validation (e.g. a
    turbine silently dropped off the feed) - something per-row checks can
    never catch since a missing row has no row to validate.
    """
    settings = get_settings()
    expected = expected_batch_row_count(
        window_start, window_end, settings.turbine_count, settings.reading_interval_seconds
    )
    if expected and actual_row_count < expected:
        missing_pct = 100 * (expected - actual_row_count) / expected
        return [
            f"completeness check: expected {expected} rows for window "
            f"[{window_start.isoformat()}, {window_end.isoformat()}), got {actual_row_count} "
            f"({missing_pct:.1f}% missing)"
        ]
    return []
