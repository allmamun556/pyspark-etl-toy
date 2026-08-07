"""
Airflow DAG: SCADA time-series ETL.

Runs every 5 minutes. Each turbine's extraction is incremental (based on
extraction_watermark), so a scheduled run only ever processes new data —
this keeps run time roughly constant as the historical dataset grows.

Task graph:
    extract_transform_validate  >>  load  >>  update_watermarks

A single upstream task does extract+transform+validate together (they're
pure/cheap and chaining them as separate Airflow tasks would just add
XCom serialization overhead for large batches); load and watermark updates
are separate tasks because they're the parts worth retrying/observing
independently.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from airflow import DAG

# Make `src` importable. In Docker, docker-compose.yml mounts ./src to
# /opt/airflow/src (a sibling of dags/), so /opt/airflow is the right root.
# Outside Docker (e.g. CI running `airflow dags test` directly against the
# repo checkout), the repo root plays the same role but sits one directory
# further up. Try both instead of hardcoding the Docker-only path, so this
# DAG parses correctly in either environment.
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


def _fetch_reference_wind_speed(conn) -> float | None:
    """
    Latest real wind speed from weather_api_readings (populated independently
    by the external_data_sources DAG), used to anchor the SCADA simulator's
    fleet instead of letting it drift on pure noise. Returns None - and the
    simulator falls back to its unanchored default - if that DAG hasn't run
    yet or its most recent reading is too stale to trust.
    """
    from sqlalchemy import text

    from src.config import get_settings

    row = conn.execute(
        text("SELECT wind_speed_ms, ts FROM weather_api_readings ORDER BY ts DESC LIMIT 1")
    ).fetchone()
    if row is None or row.wind_speed_ms is None:
        return None

    staleness = datetime.now(timezone.utc) - row.ts
    max_staleness = timedelta(minutes=get_settings().reference_wind_max_staleness_minutes)
    if staleness > max_staleness:
        return None
    return float(row.wind_speed_ms)


def _extract_transform_validate(**context) -> dict:
    from sqlalchemy import text

    from src.db.session import get_engine
    from src.extract.scada_simulator import ScadaSimulator, get_incremental_window
    from src.transform.transformers import transform_batch
    from src.utils.logging_config import get_logger
    from src.validation.validators import check_batch_completeness, validate_batch

    logger = get_logger(__name__)
    run_started_at = datetime.now(timezone.utc)
    context["ti"].xcom_push(key="run_started_at", value=run_started_at.isoformat())

    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT turbine_id, last_extracted_ts FROM extraction_watermark")
        ).fetchall()
        reference_wind_speed_ms = _fetch_reference_wind_speed(conn)
    watermarks = {r.turbine_id: r.last_extracted_ts for r in rows}

    if reference_wind_speed_ms is not None:
        logger.info(
            "anchoring simulator to reference_wind_speed_ms=%.2f from weather_api_readings",
            reference_wind_speed_ms,
        )

    window_start, window_end = get_incremental_window(watermarks)

    simulator = ScadaSimulator(reference_wind_speed_ms=reference_wind_speed_ms)
    raw = list(simulator.extract(window_start, window_end))

    for warning in check_batch_completeness(len(raw), window_start, window_end):
        logger.warning(warning, extra={"dq_check": "completeness", "run_id": context["run_id"]})

    transformed = transform_batch(raw)
    valid, failed = validate_batch(transformed)

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
                "turbine_id": f.reading.turbine_id,
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
    from src.load.loaders import load_batch_optimized
    from src.transform.transformers import TransformedReading

    ti = context["ti"]
    valid_dicts = ti.xcom_pull(key="valid_readings", task_ids="extract_transform_validate") or []
    failed_dicts = ti.xcom_pull(key="failed_readings", task_ids="extract_transform_validate") or []

    readings = [
        TransformedReading(
            turbine_id=d["turbine_id"],
            ts=dt.fromisoformat(d["ts"]),
            wind_speed_ms=d["wind_speed_ms"],
            power_kw=d["power_kw"],
            rotor_rpm=d["rotor_rpm"],
            nacelle_temp_c=d["nacelle_temp_c"],
            pitch_angle_deg=d["pitch_angle_deg"],
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
            rows_loaded += load_batch_optimized(conn, readings[i : i + 5000])

        if failed_dicts:
            from sqlalchemy import text

            conn.execute(
                text(
                    """
                    INSERT INTO scada_readings_rejects
                        (turbine_id, ts, raw_payload, reject_reason, rejected_at)
                    VALUES (:turbine_id, :ts, :raw_payload, :reject_reason, :rejected_at)
                    """
                ),
                [
                    {
                        "turbine_id": f["turbine_id"],
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
    from src.load.loaders import update_watermark

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
        turbine_ids = [
            r.turbine_id
            for r in conn.execute(text("SELECT DISTINCT turbine_id FROM scada_readings"))
        ]
        # First run: no rows yet, so fall back to a fixed turbine range.
        if not turbine_ids:
            from src.config import get_settings

            turbine_ids = [f"WT-{i:03d}" for i in range(1, get_settings().turbine_count + 1)]

        for turbine_id in turbine_ids:
            update_watermark(conn, turbine_id, datetime.fromisoformat(window_end))

        conn.execute(
            text(
                """
                INSERT INTO pipeline_run_audit
                    (dag_run_id, task_id, rows_extracted, rows_loaded, rows_rejected,
                     duration_seconds, status, started_at, finished_at)
                VALUES
                    (:dag_run_id, :task_id, :rows_extracted, :rows_loaded, :rows_rejected,
                     :duration_seconds, :status, :started_at, :finished_at)
                """
            ),
            {
                "dag_run_id": context["run_id"],
                "task_id": "scada_etl_pipeline",
                "rows_extracted": rows_extracted,
                "rows_loaded": rows_loaded,
                "rows_rejected": failed_count,
                "duration_seconds": duration_seconds,
                "status": "success",
                "started_at": run_started_at,
                "finished_at": finished_at,
            },
        )


with DAG(
    dag_id="scada_etl_pipeline",
    description="Incremental ETL for wind turbine SCADA time-series data",
    default_args=DEFAULT_ARGS,
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,  # avoid overlapping runs racing on the same watermark
    tags=["scada", "etl", "time-series"],
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
