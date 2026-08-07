"""
Transform layer for the solar plant fleet. Mirrors transformers.py's shape
exactly - pure functions, no I/O - reusing `normalize_status_code` from
there since status-code cleanup isn't source-specific.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from src.extract.solar_simulator import RawSolarReading
from src.transform.transformers import normalize_status_code


@dataclass
class TransformedSolarReading:
    plant_id: str
    ts: datetime
    irradiance_w_m2: float
    panel_temp_c: float
    dc_power_kw: float
    ac_power_kw: float
    inverter_efficiency_pct: float
    status_code: str
    is_anomalous: bool
    ingested_at: datetime

    def as_dict(self) -> dict:
        return asdict(self)


def flag_solar_anomaly(reading: RawSolarReading) -> bool:
    """
    Cross-field consistency check, independent of hard bounds: meaningful
    sun with no output, or output with no sun, is physically inconsistent
    even if each field alone is in-range - same idea as the wind
    simulator's power-vs-rotation check.
    """
    if reading.irradiance_w_m2 > 50 and reading.dc_power_kw < 0.05:
        return True
    if reading.dc_power_kw > 0.05 and reading.irradiance_w_m2 < 5:
        return True
    return False


def transform_solar_reading(raw: RawSolarReading) -> TransformedSolarReading:
    return TransformedSolarReading(
        plant_id=raw.plant_id.strip().upper(),
        ts=raw.ts,
        irradiance_w_m2=raw.irradiance_w_m2,
        panel_temp_c=raw.panel_temp_c,
        dc_power_kw=raw.dc_power_kw,
        ac_power_kw=raw.ac_power_kw,
        inverter_efficiency_pct=raw.inverter_efficiency_pct,
        status_code=normalize_status_code(raw.status_code),
        is_anomalous=flag_solar_anomaly(raw),
        ingested_at=datetime.now(timezone.utc),
    )


def transform_solar_batch(raw_readings: list[RawSolarReading]) -> list[TransformedSolarReading]:
    return [transform_solar_reading(r) for r in raw_readings]
