from datetime import datetime, timedelta, timezone

from src.transform.transformers import TransformedReading
from src.validation.validators import (
    check_batch_completeness,
    expected_batch_row_count,
    validate_batch,
    validate_reading,
)


def make_reading(**overrides) -> TransformedReading:
    defaults = dict(
        turbine_id="WT-001",
        ts=datetime(2026, 1, 1, tzinfo=timezone.utc),
        wind_speed_ms=8.0,
        power_kw=1200.0,
        rotor_rpm=12.0,
        nacelle_temp_c=25.0,
        pitch_angle_deg=0.0,
        status_code="operational",
        is_anomalous=False,
        ingested_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return TransformedReading(**defaults)


def test_valid_reading_passes():
    result = validate_reading(make_reading())
    assert result.is_valid
    assert result.reasons == []


def test_wind_speed_out_of_bounds_fails():
    result = validate_reading(make_reading(wind_speed_ms=999))
    assert not result.is_valid
    assert any("wind_speed_ms" in r for r in result.reasons)


def test_negative_power_fails():
    result = validate_reading(make_reading(power_kw=-5))
    assert not result.is_valid


def test_unrecognized_status_code_fails():
    result = validate_reading(make_reading(status_code="banana"))
    assert not result.is_valid
    assert any("status_code" in r for r in result.reasons)


def test_missing_turbine_id_fails():
    result = validate_reading(make_reading(turbine_id=""))
    assert not result.is_valid


def test_pitch_angle_out_of_range_fails():
    result = validate_reading(make_reading(pitch_angle_deg=120))
    assert not result.is_valid


def test_validate_batch_splits_valid_and_failed():
    readings = [
        make_reading(turbine_id="WT-001"),
        make_reading(turbine_id="WT-002", wind_speed_ms=999),
        make_reading(turbine_id="WT-003", rotor_rpm=-1),
    ]
    valid, failed = validate_batch(readings)
    assert len(valid) == 1
    assert len(failed) == 2
    assert valid[0].turbine_id == "WT-001"


def test_future_timestamp_beyond_skew_tolerance_fails():
    future_ts = datetime.now(timezone.utc) + timedelta(hours=1)
    result = validate_reading(make_reading(ts=future_ts))
    assert not result.is_valid
    assert any("future" in r for r in result.reasons)


def test_timestamp_within_skew_tolerance_passes():
    near_future_ts = datetime.now(timezone.utc) + timedelta(seconds=10)
    result = validate_reading(make_reading(ts=near_future_ts))
    assert result.is_valid


def test_validate_batch_rejects_duplicate_keys_keeping_first():
    ts = datetime.now(timezone.utc)
    readings = [
        make_reading(turbine_id="WT-001", ts=ts),
        make_reading(turbine_id="WT-001", ts=ts),
        make_reading(turbine_id="WT-002", ts=ts),
    ]
    valid, failed = validate_batch(readings)
    assert len(valid) == 2
    assert len(failed) == 1
    assert any("duplicate" in r for r in failed[0].reasons)


def test_expected_batch_row_count_matches_simulator_tick_logic():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    # 6 ticks of 10 minutes, 20 turbines
    assert expected_batch_row_count(start, end, turbine_count=20, interval_seconds=600) == 120


def test_check_batch_completeness_flags_shortfall(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("TURBINE_COUNT", "20")
    monkeypatch.setenv("READING_INTERVAL_SECONDS", "600")
    get_settings.cache_clear()

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)  # expects 120 rows
    warnings = check_batch_completeness(actual_row_count=100, window_start=start, window_end=end)
    assert len(warnings) == 1
    assert "expected 120" in warnings[0]
    assert "got 100" in warnings[0]

    get_settings.cache_clear()


def test_check_batch_completeness_no_warning_when_full(monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("TURBINE_COUNT", "20")
    monkeypatch.setenv("READING_INTERVAL_SECONDS", "600")
    get_settings.cache_clear()

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    warnings = check_batch_completeness(actual_row_count=120, window_start=start, window_end=end)
    assert warnings == []

    get_settings.cache_clear()
