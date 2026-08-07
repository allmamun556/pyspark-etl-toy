from datetime import datetime, timezone

from src.extract.solar_simulator import RawSolarReading
from src.transform.solar_transformers import (
    flag_solar_anomaly,
    transform_solar_batch,
    transform_solar_reading,
)


def make_raw(**overrides) -> RawSolarReading:
    defaults = dict(
        plant_id="sp-001",
        ts=datetime(2026, 6, 21, 12, tzinfo=timezone.utc),
        irradiance_w_m2=800.0,
        panel_temp_c=45.0,
        dc_power_kw=3800.0,
        ac_power_kw=3700.0,
        inverter_efficiency_pct=97.0,
        status_code="Operational",
    )
    defaults.update(overrides)
    return RawSolarReading(**defaults)


def test_transform_solar_reading_uppercases_plant_id():
    result = transform_solar_reading(make_raw(plant_id=" sp-001 "))
    assert result.plant_id == "SP-001"


def test_transform_solar_reading_sets_ingested_at():
    before = datetime.now(timezone.utc)
    result = transform_solar_reading(make_raw())
    assert result.ingested_at >= before


def test_flag_solar_anomaly_sun_without_output():
    raw = make_raw(irradiance_w_m2=600.0, dc_power_kw=0.0)
    assert flag_solar_anomaly(raw) is True


def test_flag_solar_anomaly_output_without_sun():
    raw = make_raw(irradiance_w_m2=0.0, dc_power_kw=500.0)
    assert flag_solar_anomaly(raw) is True


def test_flag_solar_anomaly_normal_operation_not_flagged():
    raw = make_raw(irradiance_w_m2=800.0, dc_power_kw=3800.0)
    assert flag_solar_anomaly(raw) is False


def test_flag_solar_anomaly_night_not_flagged():
    raw = make_raw(irradiance_w_m2=0.0, dc_power_kw=0.0)
    assert flag_solar_anomaly(raw) is False


def test_transform_solar_batch_preserves_order_and_count():
    raws = [make_raw(plant_id=f"sp-{i:03d}") for i in range(5)]
    results = transform_solar_batch(raws)
    assert len(results) == 5
    assert [r.plant_id for r in results] == [f"SP-{i:03d}" for i in range(5)]
