"""
Extract layer.

In production this module would poll an OPC-UA server, subscribe to an MQTT
broker, or query a SCADA historian's REST/SQL export. To make this project
runnable without proprietary infrastructure, it simulates a fleet of wind
turbines using a physically plausible power curve, with realistic sensor
noise, occasional stuck-sensor and out-of-range faults injected on purpose
so the validation layer downstream has real work to do.

The extractor is deliberately the ONLY module that knows about "how data
enters the system" — transform/validation/load never generate or invent
data, they only operate on what extract hands them. This is what makes it
easy to later swap the simulator for a real SCADA client without touching
anything else.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator

from src.config import get_settings


@dataclass
class RawScadaReading:
    """Unvalidated reading exactly as it would arrive from a SCADA feed."""

    turbine_id: str
    ts: datetime
    wind_speed_ms: float
    power_kw: float
    rotor_rpm: float
    nacelle_temp_c: float
    pitch_angle_deg: float
    status_code: str


# Cut-in, rated, and cut-out wind speeds for a generic ~3.3 MW turbine.
CUT_IN_MS = 3.0
RATED_MS = 12.0
CUT_OUT_MS = 25.0
RATED_POWER_KW = 3300.0


def _power_curve_kw(wind_speed_ms: float) -> float:
    """Simplified cubic power curve between cut-in and rated wind speed."""
    if wind_speed_ms < CUT_IN_MS or wind_speed_ms >= CUT_OUT_MS:
        return 0.0
    if wind_speed_ms >= RATED_MS:
        return RATED_POWER_KW
    fraction = (wind_speed_ms - CUT_IN_MS) / (RATED_MS - CUT_IN_MS)
    return RATED_POWER_KW * (fraction ** 3)


@dataclass
class TurbineState:
    """Per-turbine simulation state, so faults/noise persist across ticks."""

    turbine_id: str
    base_wind_ms: float
    stuck_sensor_ticks_remaining: int = 0
    stuck_value: dict | None = None


# Per-turbine spread around a real reference wind speed, so turbines aren't
# all identical (micro-siting / local terrain effects on a real wind farm)
# while the fleet as a whole still tracks reality instead of pure noise.
REFERENCE_WIND_SPREAD_MS = 2.0


class ScadaSimulator:
    """
    Generates one batch of readings per turbine for the requested time window,
    honoring each turbine's extraction watermark so re-runs are incremental.
    """

    def __init__(
        self, seed: int | None = None, reference_wind_speed_ms: float | None = None
    ) -> None:
        """
        reference_wind_speed_ms: when given (e.g. the latest real reading
        from weather_api_readings), each turbine's starting wind speed is
        anchored near it instead of drawn uniformly from [4, 14] - this is
        what makes the fleet's simulated wind comparable to the real
        external sources in dbt's ambient_wind_daily_comparison mart rather
        than coincidentally overlapping or not.
        """
        self.settings = get_settings()
        self._rng = random.Random(seed)
        self._turbines = [
            TurbineState(
                turbine_id=f"WT-{i:03d}",
                base_wind_ms=self._initial_wind_speed(reference_wind_speed_ms),
            )
            for i in range(1, self.settings.turbine_count + 1)
        ]

    def _initial_wind_speed(self, reference_wind_speed_ms: float | None) -> float:
        if reference_wind_speed_ms is None:
            return self._rng.uniform(4, 14)
        spread = self._rng.uniform(-REFERENCE_WIND_SPREAD_MS, REFERENCE_WIND_SPREAD_MS)
        return max(0.0, min(reference_wind_speed_ms + spread, 28.0))

    def extract(
        self, window_start: datetime, window_end: datetime
    ) -> Iterator[RawScadaReading]:
        """
        Yield raw readings for every turbine at each configured interval
        within [window_start, window_end).
        """
        interval = timedelta(seconds=self.settings.reading_interval_seconds)

        for turbine in self._turbines:
            ts = window_start
            while ts < window_end:
                yield self._generate_reading(turbine, ts)
                ts += interval

    def _generate_reading(self, turbine: TurbineState, ts: datetime) -> RawScadaReading:
        # Smooth wind variation with noise (Ornstein-Uhlenbeck-ish drift).
        turbine.base_wind_ms += self._rng.uniform(-0.4, 0.4)
        turbine.base_wind_ms = max(0.0, min(turbine.base_wind_ms, 28.0))
        wind_speed = max(0.0, turbine.base_wind_ms + self._rng.gauss(0, 0.3))

        power = _power_curve_kw(wind_speed) * self._rng.uniform(0.97, 1.03)
        rotor_rpm = 0.0 if power == 0 else min(18.0, 6.0 + (power / RATED_POWER_KW) * 10.5)
        nacelle_temp = 20 + wind_speed * 0.4 + self._rng.gauss(0, 2)
        pitch_angle = 0.0 if wind_speed < RATED_MS else min(90.0, (wind_speed - RATED_MS) * 4)

        status_code = "operational"
        if wind_speed >= CUT_OUT_MS:
            status_code = "curtailed"
            power = 0.0
            rotor_rpm = 0.0

        # --- Inject rare, realistic sensor faults (~0.5% of ticks) ---
        if turbine.stuck_sensor_ticks_remaining > 0 and turbine.stuck_value:
            turbine.stuck_sensor_ticks_remaining -= 1
            wind_speed = turbine.stuck_value["wind_speed_ms"]
            power = turbine.stuck_value["power_kw"]
            rotor_rpm = turbine.stuck_value["rotor_rpm"]
        elif self._rng.random() < 0.003:
            # Start a "stuck sensor" fault lasting a few ticks (comms glitch).
            turbine.stuck_sensor_ticks_remaining = self._rng.randint(2, 5)
            turbine.stuck_value = {
                "wind_speed_ms": wind_speed,
                "power_kw": power,
                "rotor_rpm": rotor_rpm,
            }
        elif self._rng.random() < 0.002:
            # Out-of-range spike (e.g. icing-induced anemometer error).
            power = RATED_POWER_KW * self._rng.uniform(1.2, 1.8)
            status_code = "fault"

        return RawScadaReading(
            turbine_id=turbine.turbine_id,
            ts=ts,
            wind_speed_ms=round(wind_speed, 2),
            power_kw=round(power, 2),
            rotor_rpm=round(rotor_rpm, 2),
            nacelle_temp_c=round(nacelle_temp, 2),
            pitch_angle_deg=round(pitch_angle, 2),
            status_code=status_code,
        )


def get_incremental_window(
    watermarks: dict[str, datetime], default_lookback_minutes: int = 60
) -> tuple[datetime, datetime]:
    """
    Compute the extraction window: from the oldest turbine watermark (or a
    default lookback if no watermark exists yet) up to "now". This is the
    incremental-extraction pattern that keeps re-scans bounded regardless of
    how much history has accumulated.
    """
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if not watermarks:
        return now - timedelta(minutes=default_lookback_minutes), now
    oldest = min(watermarks.values())
    return oldest, now
