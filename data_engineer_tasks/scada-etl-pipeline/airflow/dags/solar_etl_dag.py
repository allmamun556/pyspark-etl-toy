"""
Airflow DAG: solar PV plant fleet ETL.

Structurally identical to scada_etl_dag.py - same task graph, same
incremental-extraction/watermark pattern, same reference-anchoring idea
(this time against real shortwave_radiation instead of real wind speed).
Kept as its own DAG rather than folded into scada_etl_pipeline: different
simulated asset class, different curated tables, and no reason a change to
one fleet's schedule or SLA should ever touch the other's.

Task graph:
    extract_transform_validate  >>  load  >>  update_watermarks_and_audit
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from airflow import DAG

# See scada_etl_dag.py for why this checks two candidate roots instead of
# hardcoding /opt/airflow - it's what lets this DAG parse both inside
# Docker and under a bare `airflow dags test` run (e.g. in CI).
_dag_dir = Path(__file__).resolve().parent
for _root in (_dag_dir.parent, _dag_dir.parent.parent):
    if (_root / "src").is_dir():
        sys.path.insert(0, str(_root))
        break

from src.utils.alerting import notify_dag_failure  # noqa: E402

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "on_failure_callback": notify_dag_failure,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}


def _fetch_reference_irradiance(conn) -> float | None:
    """
    Latest real shortwave_radiation_w_m2 from weather_api_readings
    (populated independently by the external_data_sources DAG), used to
    anchor the solar simulator's cloud cover instead of an unanchored
    clear-sky assumption. Returns None if that DAG hasn't run yet or its
    most recent reading is too stale to trust.
    """
    from sqlalchemy import text

    from src.config import get_settings

    row = conn.execute(
        text(
            "SELECT shortwave_radiation_w_m2, ts FROM weather_api_readings ORDER BY ts DESC LIMIT 1"
        )
    ).fetchone()
    if row is None or row.shortwave_radiation_w_m2 is None:
        return None

    staleness = datetime.now(timezone.utc) - row.ts
    max_staleness = timedelta(minutes=get_settings().reference_irradiance_max_staleness_minutes)
    if staleness > max_staleness:
        return None
    return float(row.shortwave_radiation_w_m2)


def _extract_transform_validate(**context) -> dict:
    from sqlalchemy import text

    from src.db.session import get_engine
    from src.extract.solar_simulator import SolarPlantSimulator, get_incremental_window
    from src.transform.solar_transformers import transform_solar_batch
    from src.utils.logging_config import get_logger
    from src.validation.solar_validators import check_solar_batch_completeness, validate_solar_batch

    logger = get_logger(__name__)
    run_started_at = datetime.now(timezone.utc)
    context["ti"].xcom_push(key="run_started_at", value=run_started_at.isoformat())

    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT plant_id, last_extracted_ts FROM solar_extraction_watermark")
        ).fetchall()
        reference_irradiance_w_m2 = _fetch_reference_irradiance(conn)
    watermarks = {r.plant_id: r.last_extracted_ts for r in rows}

    if reference_irradiance_w_m2 is not None:
        logger.info(
            "anchoring simulator to reference_irradiance_w_m2=%.1f from weather_api_readings",
            reference_irradiance_w_m2,
        )

    window_start, window_end = get_incremental_window(watermarks)

    simulator = SolarPlantSimulator(reference_irradiance_w_m2=reference_irradiance_w_m2)
    raw = list(simulator.extract(window_start, window_end))

    for warning in check_solar_batch_completeness(len(raw), window_start, window_end):
        logger.warning(warning, extra={"dq_check": "completeness", "run_id": context["run_id"]})

    transformed = transform_solar_batch(raw)
    valid, failed = validate_solar_batch(transformed)

    context["ti"].xcom_push(key="window_end", value=window_end.isoformat())
    context["ti"].xcom_push(key="rows_extracted", value=len(raw))
    context["ti"].xcom_push(
        key="valid_readings",
        value=[
            r.as_dict() | {"ts": r.ts.isoformat(), "ingested_at": r.ingested_at.isoformat()}
            for r in valid
        ],
    )
    context["ti"].xcom_push(key="failed_count", value=len(failed))
    context["ti"].xcom_push(
        key="failed_readings",
        value=[
            {
                "plant_id": f.reading.plant_id,
                "ts": f.reading.ts.isoformat(),
                "raw_payload": str(f.reading.as_dict()),
                "reasons": f.reasons,
            }
            for f in failed
        ],
    )
    return {"rows_extracted": len(raw), "rows_valid": len(valid), "rows_failed": len(failed)}


def _load(**context) -> dict:
    from datetime import datetime as dt

    from src.db.session import get_engine
    from src.load.solar_loaders import load_solar_batch_optimized
    from src.transform.solar_transformers import TransformedSolarReading

    ti = context["ti"]
    valid_dicts = ti.xcom_pull(key="valid_readings", task_ids="extract_transform_validate") or []
    failed_dicts = ti.xcom_pull(key="failed_readings", task_ids="extract_transform_validate") or []

    readings = [
        TransformedSolarReading(
            plant_id=d["plant_id"],
            ts=dt.fromisoformat(d["ts"]),
            irradiance_w_m2=d["irradiance_w_m2"],
            panel_temp_c=d["panel_temp_c"],
            dc_power_kw=d["dc_power_kw"],
            ac_power_kw=d["ac_power_kw"],
            inverter_efficiency_pct=d["inverter_efficiency_pct"],
            status_code=d["status_code"],
            is_anomalous=d["is_anomalous"],
            ingested_at=dt.fromisoformat(d["ingested_at"]),
        )
        for d in valid_dicts
    ]

    engine = get_engine()
    rows_loaded = 0
    with engine.begin() as conn:
        for i in range(0, len(readings), 5000):
            rows_loaded += load_solar_batch_optimized(conn, readings[i : i + 5000])

        if failed_dicts:
            from sqlalchemy import text

            conn.execute(
                text(
                    """
                    INSERT INTO solar_readings_rejects
                        (plant_id, ts, raw_payload, reject_reason, rejected_at)
                    VALUES (:plant_id, :ts, :raw_payload, :reject_reason, :rejected_at)
                    """
                ),
                [
                    {
                        "plant_id": f["plant_id"],
                        "ts": dt.fromisoformat(f["ts"]),
                        "raw_payload": f["raw_payload"],
                        "reject_reason": "; ".join(f["reasons"]),
                        "rejected_at": datetime.now(timezone.utc),
                    }
                    for f in failed_dicts
                ],
            )

    ti.xcom_push(key="rows_loaded", value=rows_loaded)
    return {"rows_loaded": rows_loaded, "rows_rejected": len(failed_dicts)}


def _update_watermarks_and_audit(**context) -> None:
    from sqlalchemy import text

    from src.db.session import get_engine
    from src.load.loaders import record_run_audit
    from src.load.solar_loaders import update_solar_watermark

    ti = context["ti"]
    window_end = ti.xcom_pull(key="window_end", task_ids="extract_transform_validate")
    rows_extracted = ti.xcom_pull(key="rows_extracted", task_ids="extract_transform_validate") or 0
    rows_loaded = ti.xcom_pull(key="rows_loaded", task_ids="load") or 0
    failed_count = ti.xcom_pull(key="failed_count", task_ids="extract_transform_validate") or 0
    run_started_at = datetime.fromisoformat(
        ti.xcom_pull(key="run_started_at", task_ids="extract_transform_validate")
    )
    finished_at = datetime.now(timezone.utc)
    duration_seconds = (finished_at - run_started_at).total_seconds()

    engine = get_engine()
    with engine.begin() as conn:
        plant_ids = [
            r.plant_id for r in conn.execute(text("SELECT DISTINCT plant_id FROM solar_readings"))
        ]
        # First run: no rows yet, so fall back to a fixed plant range.
        if not plant_ids:
            from src.config import get_settings

            plant_ids = [f"SP-{i:03d}" for i in range(1, get_settings().solar_plant_count + 1)]

        for plant_id in plant_ids:
            update_solar_watermark(conn, plant_id, datetime.fromisoformat(window_end))

        record_run_audit(
            conn,
            dag_run_id=context["run_id"],
            task_id="solar_etl_pipeline",
            rows_extracted=rows_extracted,
            rows_loaded=rows_loaded,
            rows_rejected=failed_count,
            duration_seconds=duration_seconds,
            status="success",
            started_at=run_started_at,
            finished_at=finished_at,
        )


with DAG(
    dag_id="solar_etl_pipeline",
    description="Incremental ETL for simulated solar PV plant time-series data",
    default_args=DEFAULT_ARGS,
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["solar", "etl", "time-series"],
) as dag:
    extract_transform_validate = PythonOperator(
        task_id="extract_transform_validate",
        python_callable=_extract_transform_validate,
        sla=timedelta(minutes=4),
    )

    load = PythonOperator(
        task_id="load",
        python_callable=_load,
        sla=timedelta(minutes=3),
    )

    update_watermarks_and_audit = PythonOperator(
        task_id="update_watermarks_and_audit",
        python_callable=_update_watermarks_and_audit,
    )

    extract_transform_validate >> load >> update_watermarks_and_audit
