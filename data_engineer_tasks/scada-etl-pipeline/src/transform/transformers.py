"""
Transform layer.

Pure functions only: given raw readings in, cleaned/enriched readings out.
No I/O here (no DB, no network) — that's what makes this module trivially
unit-testable and safe to run in parallel.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from src.extract.scada_simulator import RawScadaReading


@dataclass
class TransformedReading:
    turbine_id: str
    ts: datetime
    wind_speed_ms: float
    power_kw: float
    rotor_rpm: float
    nacelle_temp_c: float
    pitch_angle_deg: float
    status_code: str
    is_anomalous: bool
    ingested_at: datetime

    def as_dict(self) -> dict:
        return asdict(self)


def normalize_status_code(status_code: str) -> str:
    """Defensive normalization: SCADA vendors are inconsistent about casing/spacing."""
    return status_code.strip().lower().replace(" ", "_")


def flag_statistical_anomaly(reading: RawScadaReading) -> bool:
    """
    Lightweight anomaly flag independent of the hard validation bounds:
    a turbine reporting non-zero power at (near) zero rotor RPM, or vice
    versa, is inconsistent even if each field individually is in-range.
    """
    if reading.power_kw > 50 and reading.rotor_rpm < 1.0:
        return True
    if reading.rotor_rpm > 3.0 and reading.power_kw <= 0:
        return True
    return False


def transform_reading(raw: RawScadaReading) -> TransformedReading:
    return TransformedReading(
        turbine_id=raw.turbine_id.strip().upper(),
        ts=raw.ts,
        wind_speed_ms=raw.wind_speed_ms,
        power_kw=raw.power_kw,
        rotor_rpm=raw.rotor_rpm,
        nacelle_temp_c=raw.nacelle_temp_c,
        pitch_angle_deg=raw.pitch_angle_deg,
        status_code=normalize_status_code(raw.status_code),
        is_anomalous=flag_statistical_anomaly(raw),
        ingested_at=datetime.now(timezone.utc),
    )


def transform_batch(raw_readings: list[RawScadaReading]) -> list[TransformedReading]:
    return [transform_reading(r) for r in raw_readings]
