from datetime import datetime, timedelta, timezone

from src.transform.solar_transformers import TransformedSolarReading
from src.validation.solar_validators import (
    check_solar_batch_completeness,
    expected_solar_batch_row_count,
    validate_solar_batch,
    validate_solar_reading,
)


def make_reading(**overrides) -> TransformedSolarReading:
    defaults = dict(
        plant_id="SP-001",
        ts=datetime(2026, 6, 21, 12, tzinfo=timezone.utc),
        irradiance_w_m2=800.0,
        panel_temp_c=45.0,
        dc_power_kw=3800.0,
        ac_power_kw=3700.0,
        inverter_efficiency_pct=97.0,
        status_code="operational",
        is_anomalous=False,
        ingested_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return TransformedSolarReading(**defaults)


def test_valid_solar_reading_passes():
    result = validate_solar_reading(make_reading())
    assert result.is_valid
    assert result.reasons == []


def test_irradiance_out_of_bounds_fails():
    result = validate_solar_reading(make_reading(irradiance_w_m2=9999))
    assert not result.is_valid
    assert any("irradiance_w_m2" in r for r in result.reasons)


def test_panel_temp_out_of_bounds_fails():
    result = validate_solar_reading(make_reading(panel_temp_c=150))
    assert not result.is_valid
    assert any("panel_temp_c" in r for r in result.reasons)


def test_ac_power_exceeding_dc_power_fails():
    result = validate_solar_reading(make_reading(dc_power_kw=100, ac_power_kw=500))
    assert not result.is_valid
    assert any("exceeds dc_power_kw" in r for r in result.reasons)


def test_unrecognized_status_code_fails():
    result = validate_solar_reading(make_reading(status_code="banana"))
    assert not result.is_valid
    assert any("status_code" in r for r in result.reasons)


def test_missing_plant_id_fails():
    result = validate_solar_reading(make_reading(plant_id=""))
    assert not result.is_valid


def test_night_status_is_valid():
    result = validate_solar_reading(
        make_reading(status_code="night", irradiance_w_m2=0, dc_power_kw=0, ac_power_kw=0)
    )
    assert result.is_valid


def test_future_timestamp_beyond_skew_tolerance_fails():
    future_ts = datetime.now(timezone.utc) + timedelta(hours=1)
    result = validate_solar_reading(make_reading(ts=future_ts))
    assert not result.is_valid
    assert any("future" in r for r in result.reasons)


def test_validate_solar_batch_rejects_duplicate_keys_keeping_first():
    ts = datetime.now(timezone.utc)
    readings = [
        make_reading(plant_id="SP-001", ts=ts),
        make_reading(plant_id="SP-001", ts=ts),
        make_reading(plant_id="SP-002", ts=ts),
    ]
    valid, failed = validate_solar_batch(readings)
    assert len(valid) == 2
    assert len(failed) == 1
    assert any("duplicate" in r for r in failed[0].reasons)


def test_expected_solar_batch_row_count_matches_simulator_tick_logic():
    start = datetime(2026, 6, 21, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    assert expected_solar_batch_row_count(start, end, plant_count=8, interval_seconds=600) == 48


def test_check_solar_batch_completeness_flags_shortfall(monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("SOLAR_PLANT_COUNT", "8")
    monkeypatch.setenv("READING_INTERVAL_SECONDS", "600")
    get_settings.cache_clear()

    start = datetime(2026, 6, 21, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)  # expects 48 rows
    warnings = check_solar_batch_completeness(
        actual_row_count=40, window_start=start, window_end=end
    )
    assert len(warnings) == 1
    assert "expected 48" in warnings[0]
    assert "got 40" in warnings[0]

    get_settings.cache_clear()
