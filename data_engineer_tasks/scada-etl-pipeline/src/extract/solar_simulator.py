"""
Extract layer: simulated solar PV plant fleet.

Same reasoning as src/extract/scada_simulator.py: real per-plant inverter
telemetry is proprietary to solar operators, so this simulates a fleet
using a physically plausible clear-sky irradiance model, NOCT-based panel
heating, and a standard PV temperature-derating curve, with realistic
faults injected on purpose. This is deliberately the only module that knows
"how solar data enters the system" - transform/validation/load never
generate data, only operate on what this hands them.

`get_incremental_window` is reused from scada_simulator - it's watermark
logic with no turbine/plant-specific behavior, so duplicating it here would
just be drift risk for no benefit.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator

from src.config import get_settings

__all__ = ["RawSolarReading", "PlantState", "SolarPlantSimulator", "get_incremental_window"]

from src.extract.scada_simulator import get_incremental_window  # noqa: F401


@dataclass
class RawSolarReading:
    """Unvalidated reading exactly as it would arrive from an inverter/SCADA feed."""

    plant_id: str
    ts: datetime
    irradiance_w_m2: float
    panel_temp_c: float
    dc_power_kw: float
    ac_power_kw: float
    inverter_efficiency_pct: float
    status_code: str


# Clear-sky model constants. Sunrise/sunset are fixed UTC hours rather than
# computed from solar position for the plant's actual longitude/date - a
# deliberate simplification, noted here rather than left silently wrong.
SUNRISE_HOUR = 6.0
SUNSET_HOUR = 18.0
PEAK_CLEAR_SKY_W_M2 = 950.0
# Nominal Operating Cell Temperature: panel temp at 800 W/m2, 20C ambient,
# 1 m/s wind - a standard PV datasheet spec used to model panel self-heating.
NOCT_C = 45.0
# Crystalline-silicon temperature coefficient: power output drops ~0.4% per
# degree C the panel runs above the 25C Standard Test Conditions baseline.
TEMP_COEFFICIENT_PCT_PER_C = 0.4


def _clear_sky_irradiance(ts: datetime) -> float:
    """Sinusoidal clear-sky irradiance curve: zero outside daylight hours."""
    hour = ts.hour + ts.minute / 60.0
    if hour <= SUNRISE_HOUR or hour >= SUNSET_HOUR:
        return 0.0
    daylight_fraction = (hour - SUNRISE_HOUR) / (SUNSET_HOUR - SUNRISE_HOUR)
    return PEAK_CLEAR_SKY_W_M2 * math.sin(math.pi * daylight_fraction)


@dataclass
class PlantState:
    """Per-plant simulation state, so cloud cover/faults persist across ticks."""

    plant_id: str
    # 1.0 = clear sky, lower = clouds. Drifts like the wind simulator's
    # base_wind_ms so a plant's cloud cover is sticky, not independent noise
    # every tick. Always set explicitly by SolarPlantSimulator.__init__ (via
    # _initial_cloud_factor), which is what makes it seed-reproducible.
    cloud_factor: float
    stuck_sensor_ticks_remaining: int = 0
    stuck_value: dict | None = None


class SolarPlantSimulator:
    """
    Generates one batch of readings per plant for the requested time window,
    honoring each plant's extraction watermark so re-runs are incremental.
    """

    def __init__(
        self, seed: int | None = None, reference_irradiance_w_m2: float | None = None
    ) -> None:
        """
        reference_irradiance_w_m2: when given (e.g. the latest real
        shortwave_radiation reading from weather_api_readings), each
        plant's cloud factor is anchored so simulated output tracks
        real conditions instead of an independent clear-sky assumption -
        mirrors ScadaSimulator's reference_wind_speed_ms anchoring.
        """
        self.settings = get_settings()
        self._rng = random.Random(seed)
        self._reference_irradiance_w_m2 = reference_irradiance_w_m2
        self._plants = [
            PlantState(
                plant_id=f"SP-{i:03d}",
                cloud_factor=self._initial_cloud_factor(),
            )
            for i in range(1, self.settings.solar_plant_count + 1)
        ]

    def _initial_cloud_factor(self) -> float:
        if self._reference_irradiance_w_m2 is None or self._reference_irradiance_w_m2 <= 0:
            return self._rng.uniform(0.6, 1.0)
        # Back out an implied cloud factor from the real reading against
        # what clear-sky would predict for right now, then add a small
        # per-plant spread (each plant sees slightly different local cloud).
        implied = self._reference_irradiance_w_m2 / max(PEAK_CLEAR_SKY_W_M2, 1.0)
        spread = self._rng.uniform(-0.1, 0.1)
        return max(0.15, min(implied + spread, 1.05))

    def extract(
        self, window_start: datetime, window_end: datetime
    ) -> Iterator[RawSolarReading]:
        """
        Yield raw readings for every plant at each configured interval
        within [window_start, window_end).
        """
        interval = timedelta(seconds=self.settings.reading_interval_seconds)

        for plant in self._plants:
            ts = window_start
            while ts < window_end:
                yield self._generate_reading(plant, ts)
                ts += interval

    def _generate_reading(self, plant: PlantState, ts: datetime) -> RawSolarReading:
        # Cloud cover drifts slowly (Ornstein-Uhlenbeck-ish), same pattern
        # as the wind simulator's base_wind_ms.
        plant.cloud_factor += self._rng.uniform(-0.05, 0.05)
        plant.cloud_factor = max(0.15, min(plant.cloud_factor, 1.05))

        clear_sky = _clear_sky_irradiance(ts)
        # Sensor noise only applies when there's actual daylight to measure -
        # true night (clear_sky == 0) must read exactly 0, not a coin-flip
        # around 0 that occasionally produces "operational" output in the dark.
        irradiance = (
            max(0.0, clear_sky * plant.cloud_factor + self._rng.gauss(0, 8))
            if clear_sky > 0
            else 0.0
        )

        ambient_temp = 12 + 8 * max(0.0, math.sin(math.pi * ((ts.hour + ts.minute / 60) / 24)))
        panel_temp = ambient_temp + (NOCT_C - 20.0) / 800.0 * irradiance + self._rng.gauss(0, 1.5)

        derate = max(
            0.5, 1 - (TEMP_COEFFICIENT_PCT_PER_C / 100) * max(0.0, panel_temp - 25.0)
        )
        dc_power = (
            self.settings.solar_capacity_kwp
            * (irradiance / 1000.0)
            * derate
            * self._rng.uniform(0.97, 1.03)
        )
        dc_power = max(0.0, dc_power)

        if dc_power < 0.05:
            inverter_efficiency_pct = 0.0
        else:
            # Inverters are inefficient near zero load and plateau quickly -
            # ramp efficiency up over the first ~15% of rated capacity.
            ramp = min(1.0, dc_power / (self.settings.solar_capacity_kwp * 0.15))
            inverter_efficiency_pct = 90.0 + 8.0 * ramp

        ac_power = min(
            dc_power * inverter_efficiency_pct / 100.0,
            self.settings.solar_inverter_ac_capacity_kw,
        )

        status_code = "operational" if dc_power > 0.05 else "night"

        # --- Inject rare, realistic faults (~0.5% of ticks) ---
        if plant.stuck_sensor_ticks_remaining > 0 and plant.stuck_value:
            plant.stuck_sensor_ticks_remaining -= 1
            irradiance = plant.stuck_value["irradiance_w_m2"]
            dc_power = plant.stuck_value["dc_power_kw"]
            ac_power = plant.stuck_value["ac_power_kw"]
        elif self._rng.random() < 0.003:
            # Stuck irradiance sensor (comms glitch), lasting a few ticks.
            plant.stuck_sensor_ticks_remaining = self._rng.randint(2, 5)
            plant.stuck_value = {
                "irradiance_w_m2": irradiance,
                "dc_power_kw": dc_power,
                "ac_power_kw": ac_power,
            }
        elif dc_power > 0.05 and self._rng.random() < 0.002:
            # Inverter trip: full sun available, but a grid fault or
            # protective shutdown drops AC output to zero.
            ac_power = 0.0
            status_code = "fault"

        return RawSolarReading(
            plant_id=plant.plant_id,
            ts=ts,
            irradiance_w_m2=round(irradiance, 2),
            panel_temp_c=round(panel_temp, 2),
            dc_power_kw=round(dc_power, 2),
            ac_power_kw=round(ac_power, 2),
            inverter_efficiency_pct=round(inverter_efficiency_pct, 2),
            status_code=status_code,
        )
