from datetime import datetime, timedelta, timezone

from src.extract.scada_simulator import (
    CUT_IN_MS,
    CUT_OUT_MS,
    RATED_MS,
    RATED_POWER_KW,
    REFERENCE_WIND_SPREAD_MS,
    ScadaSimulator,
    _power_curve_kw,
    get_incremental_window,
)


def test_power_curve_zero_below_cut_in():
    assert _power_curve_kw(CUT_IN_MS - 0.1) == 0.0


def test_power_curve_zero_at_and_above_cut_out():
    assert _power_curve_kw(CUT_OUT_MS) == 0.0
    assert _power_curve_kw(CUT_OUT_MS + 5) == 0.0


def test_power_curve_rated_at_and_above_rated_speed():
    assert _power_curve_kw(RATED_MS) == RATED_POWER_KW
    assert _power_curve_kw(RATED_MS + 3) == RATED_POWER_KW


def test_power_curve_monotonic_between_cut_in_and_rated():
    speeds = [CUT_IN_MS + i * 0.5 for i in range(int((RATED_MS - CUT_IN_MS) / 0.5))]
    powers = [_power_curve_kw(s) for s in speeds]
    assert powers == sorted(powers)


def test_simulator_generates_reading_per_turbine_per_interval():
    sim = ScadaSimulator(seed=1)
    sim.settings.turbine_count = 3
    sim.settings.reading_interval_seconds = 600
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)  # 6 intervals of 10 min
    readings = list(sim.extract(start, end))
    # 3 turbines set at init time, so we validate turbine count from _turbines
    n_turbines = len(sim._turbines)
    expected = n_turbines * 6
    assert len(readings) == expected


def test_simulator_readings_within_broad_physical_bounds():
    sim = ScadaSimulator(seed=7)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    readings = list(sim.extract(start, end))
    for r in readings:
        assert 0 <= r.wind_speed_ms <= 30
        assert 0 <= r.rotor_rpm <= 20


def test_get_incremental_window_no_watermarks_uses_default_lookback():
    start, end = get_incremental_window({}, default_lookback_minutes=30)
    assert (end - start) == timedelta(minutes=30)


def test_simulator_without_reference_uses_wide_random_range():
    sim = ScadaSimulator(seed=3)
    assert all(4 <= t.base_wind_ms <= 14 for t in sim._turbines)


def test_simulator_anchors_turbines_to_reference_wind_speed():
    reference = 10.0
    sim = ScadaSimulator(seed=3, reference_wind_speed_ms=reference)
    for turbine in sim._turbines:
        assert reference - REFERENCE_WIND_SPREAD_MS <= turbine.base_wind_ms
        assert turbine.base_wind_ms <= reference + REFERENCE_WIND_SPREAD_MS


def test_simulator_reference_wind_speed_is_clamped_to_physical_bounds():
    sim = ScadaSimulator(seed=3, reference_wind_speed_ms=0.5)
    assert all(t.base_wind_ms >= 0.0 for t in sim._turbines)


def test_simulator_base_wind_ms_is_deterministic_with_seed():
    sim_a = ScadaSimulator(seed=42, reference_wind_speed_ms=8.0)
    sim_b = ScadaSimulator(seed=42, reference_wind_speed_ms=8.0)
    assert [t.base_wind_ms for t in sim_a._turbines] == [t.base_wind_ms for t in sim_b._turbines]


def test_get_incremental_window_uses_oldest_watermark():
    now = datetime.now(timezone.utc)
    watermarks = {
        "WT-001": now - timedelta(minutes=10),
        "WT-002": now - timedelta(minutes=25),
    }
    start, _ = get_incremental_window(watermarks)
    assert start == now - timedelta(minutes=25)
