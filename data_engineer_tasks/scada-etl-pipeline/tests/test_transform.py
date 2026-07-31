from datetime import datetime, timezone

from src.extract.scada_simulator import RawScadaReading
from src.transform.transformers import (
    flag_statistical_anomaly,
    normalize_status_code,
    transform_batch,
    transform_reading,
)


def make_raw(**overrides) -> RawScadaReading:
    defaults = dict(
        turbine_id="wt-001",
        ts=datetime(2026, 1, 1, tzinfo=timezone.utc),
        wind_speed_ms=8.0,
        power_kw=1200.0,
        rotor_rpm=12.0,
        nacelle_temp_c=25.0,
        pitch_angle_deg=0.0,
        status_code="Operational",
    )
    defaults.update(overrides)
    return RawScadaReading(**defaults)


def test_normalize_status_code_lowercases_and_strips():
    assert normalize_status_code(" Operational ") == "operational"
    assert normalize_status_code("Wind Fault") == "wind_fault"


def test_transform_reading_uppercases_turbine_id():
    result = transform_reading(make_raw(turbine_id=" wt-001 "))
    assert result.turbine_id == "WT-001"


def test_transform_reading_sets_ingested_at():
    before = datetime.now(timezone.utc)
    result = transform_reading(make_raw())
    assert result.ingested_at >= before


def test_flag_statistical_anomaly_power_without_rotation():
    raw = make_raw(power_kw=500, rotor_rpm=0.0)
    assert flag_statistical_anomaly(raw) is True


def test_flag_statistical_anomaly_rotation_without_power():
    raw = make_raw(power_kw=0.0, rotor_rpm=10.0)
    assert flag_statistical_anomaly(raw) is True


def test_flag_statistical_anomaly_normal_operation_not_flagged():
    raw = make_raw(power_kw=1200, rotor_rpm=12.0)
    assert flag_statistical_anomaly(raw) is False


def test_transform_batch_preserves_order_and_count():
    raws = [make_raw(turbine_id=f"wt-{i:03d}") for i in range(5)]
    results = transform_batch(raws)
    assert len(results) == 5
    assert [r.turbine_id for r in results] == [f"WT-{i:03d}" for i in range(5)]
