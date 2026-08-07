from datetime import datetime, timedelta, timezone

from src.extract.solar_simulator import (
    PEAK_CLEAR_SKY_W_M2,
    SUNRISE_HOUR,
    SUNSET_HOUR,
    SolarPlantSimulator,
    _clear_sky_irradiance,
)


def test_clear_sky_irradiance_zero_before_sunrise():
    ts = datetime(2026, 6, 21, int(SUNRISE_HOUR) - 1, tzinfo=timezone.utc)
    assert _clear_sky_irradiance(ts) == 0.0


def test_clear_sky_irradiance_zero_after_sunset():
    ts = datetime(2026, 6, 21, int(SUNSET_HOUR) + 1, tzinfo=timezone.utc)
    assert _clear_sky_irradiance(ts) == 0.0


def test_clear_sky_irradiance_peaks_near_solar_noon():
    noon = datetime(2026, 6, 21, 12, tzinfo=timezone.utc)
    morning = datetime(2026, 6, 21, 8, tzinfo=timezone.utc)
    assert _clear_sky_irradiance(noon) > _clear_sky_irradiance(morning)
    assert _clear_sky_irradiance(noon) <= PEAK_CLEAR_SKY_W_M2 + 1e-6


def test_simulator_generates_reading_per_plant_per_interval():
    sim = SolarPlantSimulator(seed=1)
    sim.settings.solar_plant_count = 4
    sim.settings.reading_interval_seconds = 600
    start = datetime(2026, 6, 21, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)  # 6 intervals of 10 min
    readings = list(sim.extract(start, end))
    n_plants = len(sim._plants)
    assert len(readings) == n_plants * 6


def test_true_night_readings_are_exactly_zero():
    sim = SolarPlantSimulator(seed=3)
    start = datetime(2026, 6, 21, 1, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    readings = list(sim.extract(start, end))
    assert readings
    for r in readings:
        assert r.irradiance_w_m2 == 0.0
        assert r.dc_power_kw == 0.0
        assert r.ac_power_kw == 0.0
        assert r.status_code == "night"


def test_daytime_readings_within_physical_bounds():
    sim = SolarPlantSimulator(seed=7)
    start = datetime(2026, 6, 21, 11, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    readings = list(sim.extract(start, end))
    for r in readings:
        assert 0 <= r.irradiance_w_m2 <= 1200
        assert 0 <= r.ac_power_kw <= r.dc_power_kw + 0.5


def test_simulator_without_reference_uses_wide_cloud_range():
    sim = SolarPlantSimulator(seed=5)
    assert all(0.6 <= p.cloud_factor <= 1.0 for p in sim._plants)


def test_simulator_anchors_to_reference_irradiance():
    # 475 W/m2 implies a cloud factor near 0.5 against the 950 W/m2 peak.
    sim = SolarPlantSimulator(seed=5, reference_irradiance_w_m2=475.0)
    assert all(0.35 <= p.cloud_factor <= 0.65 for p in sim._plants)


def test_simulator_cloud_factor_is_deterministic_with_seed():
    sim_a = SolarPlantSimulator(seed=42, reference_irradiance_w_m2=400.0)
    sim_b = SolarPlantSimulator(seed=42, reference_irradiance_w_m2=400.0)
    assert [p.cloud_factor for p in sim_a._plants] == [p.cloud_factor for p in sim_b._plants]
