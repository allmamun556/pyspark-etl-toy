"""
Airflow DAG: real external data sources.

Two independent tasks, each hitting a real, free, no-key HTTP endpoint:
    - extract_load_weather: Open-Meteo current weather (HTTP API source)
    - extract_load_buoy:    NOAA NDBC ocean buoy telemetry (IoT source)

Kept as a separate DAG from scada_etl_pipeline rather than extra tasks
bolted onto it: different upstream systems, different failure domains (a
NOAA outage shouldn't retry-storm the turbine pipeline), and a coarser
schedule makes sense since ambient weather doesn't change every 5 minutes.
Both write into their own tables (see migrations/versions/0002_*), so
correlating them against scada_readings is a downstream (dbt/dashboard)
concern, not this DAG's.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from airflow import DAG

# See scada_etl_dag.py for why this checks two candidate roots instead of
# hardcoding /opt/airflow.
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


def _extract_load_weather(**context) -> dict:
    from src.db.session import get_engine
    from src.extract.weather_api_extractor import fetch_current_weather
    from src.load.external_loaders import load_weather_reading, record_external_run_audit
    from src.utils.logging_config import get_logger
    from src.validation.external_validators import validate_weather_reading

    logger = get_logger(__name__)
    started_at = datetime.now(timezone.utc)
    status, rows_loaded, rows_rejected = "success", 0, 0

    try:
        reading = fetch_current_weather()
        result = validate_weather_reading(reading)
        if result.is_valid:
            with get_engine().begin() as conn:
                load_weather_reading(conn, reading, ingested_at=datetime.now(timezone.utc))
            rows_loaded = 1
        else:
            rows_rejected = 1
            logger.warning(
                "weather reading failed validation: %s",
                "; ".join(result.reasons),
                extra={"dq_check": "external_validation", "source": "open-meteo"},
            )
    except Exception:
        status = "failed"
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        with get_engine().begin() as conn:
            record_external_run_audit(
                conn,
                dag_run_id=context["run_id"],
                source="open-meteo",
                rows_fetched=1,
                rows_loaded=rows_loaded,
                rows_rejected=rows_rejected,
                duration_seconds=(finished_at - started_at).total_seconds(),
                status=status,
                started_at=started_at,
                finished_at=finished_at,
            )

    return {"rows_loaded": rows_loaded, "rows_rejected": rows_rejected}


def _extract_load_buoy(**context) -> dict:
    from src.db.session import get_engine
    from src.extract.iot_buoy_extractor import fetch_latest_buoy_reading
    from src.load.external_loaders import load_buoy_reading, record_external_run_audit
    from src.utils.logging_config import get_logger
    from src.validation.external_validators import validate_buoy_reading

    logger = get_logger(__name__)
    started_at = datetime.now(timezone.utc)
    status, rows_loaded, rows_rejected = "success", 0, 0

    try:
        reading = fetch_latest_buoy_reading()
        result = validate_buoy_reading(reading)
        if result.is_valid:
            with get_engine().begin() as conn:
                load_buoy_reading(conn, reading, ingested_at=datetime.now(timezone.utc))
            rows_loaded = 1
        else:
            rows_rejected = 1
            logger.warning(
                "buoy reading failed validation: %s",
                "; ".join(result.reasons),
                extra={"dq_check": "external_validation", "source": "noaa-ndbc"},
            )
    except Exception:
        status = "failed"
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        with get_engine().begin() as conn:
            record_external_run_audit(
                conn,
                dag_run_id=context["run_id"],
                source="noaa-ndbc",
                rows_fetched=1,
                rows_loaded=rows_loaded,
                rows_rejected=rows_rejected,
                duration_seconds=(finished_at - started_at).total_seconds(),
                status=status,
                started_at=started_at,
                finished_at=finished_at,
            )

    return {"rows_loaded": rows_loaded, "rows_rejected": rows_rejected}


with DAG(
    dag_id="external_data_sources",
    description="Real HTTP weather API (Open-Meteo) + real IoT ocean buoy (NOAA NDBC)",
    default_args=DEFAULT_ARGS,
    schedule_interval=timedelta(minutes=15),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["external", "weather", "iot", "http-api"],
) as dag:
    extract_load_weather = PythonOperator(
        task_id="extract_load_weather",
        python_callable=_extract_load_weather,
        sla=timedelta(minutes=5),
    )

    extract_load_buoy = PythonOperator(
        task_id="extract_load_buoy",
        python_callable=_extract_load_buoy,
        sla=timedelta(minutes=5),
    )

    # Independent sources - no ordering dependency between them.
    [extract_load_weather, extract_load_buoy]
