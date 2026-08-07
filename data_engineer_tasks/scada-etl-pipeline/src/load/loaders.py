"""
Load layer.

The optimized path:
  1. COPY the batch into an UNLOGGED staging table (fast, bulk, no per-row
     round trip).
  2. A single `INSERT ... SELECT ... FROM staging ON CONFLICT (turbine_id, ts)
     DO UPDATE` moves it into the curated table, inside one transaction.
  3. Truncate staging.

This is dramatically faster than row-by-row INSERTs (see scripts/benchmark.py)
and is idempotent: replaying the same batch (e.g. after an Airflow retry)
converges to the same end state instead of creating duplicates.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.transform.transformers import TransformedReading
from src.validation.validators import ValidationResult

STAGING_TABLE = "scada_readings_staging"


def _reading_to_csv_row(r: TransformedReading) -> list:
    return [
        r.turbine_id,
        r.ts.isoformat(),
        r.wind_speed_ms,
        r.power_kw,
        r.rotor_rpm,
        r.nacelle_temp_c,
        r.pitch_angle_deg,
        r.status_code,
        r.is_anomalous,
        r.ingested_at.isoformat(),
    ]


def load_batch_optimized(conn: Connection, readings: list[TransformedReading]) -> int:
    """
    Batch-load via COPY + staged UPSERT. Returns rows written to the
    curated table (post-dedup, since a batch may legitimately contain
    updates to previously-ingested rows).
    """
    if not readings:
        return 0

    buf = io.StringIO()
    writer = csv.writer(buf)
    for r in readings:
        writer.writerow(_reading_to_csv_row(r))
    buf.seek(0)

    raw_conn = conn.connection
    cur = raw_conn.cursor()
    cur.copy_expert(
        f"""
        COPY {STAGING_TABLE}
            (turbine_id, ts, wind_speed_ms, power_kw, rotor_rpm,
             nacelle_temp_c, pitch_angle_deg, status_code, is_anomalous, ingested_at)
        FROM STDIN WITH (FORMAT csv)
        """,
        buf,
    )

    result = conn.execute(
        text(
            f"""
            INSERT INTO scada_readings
                (turbine_id, ts, wind_speed_ms, power_kw, rotor_rpm,
                 nacelle_temp_c, pitch_angle_deg, status_code, is_anomalous, ingested_at)
            SELECT turbine_id, ts, wind_speed_ms, power_kw, rotor_rpm,
                   nacelle_temp_c, pitch_angle_deg, status_code, is_anomalous, ingested_at
            FROM {STAGING_TABLE}
            ON CONFLICT (turbine_id, ts) DO UPDATE SET
                wind_speed_ms = EXCLUDED.wind_speed_ms,
                power_kw = EXCLUDED.power_kw,
                rotor_rpm = EXCLUDED.rotor_rpm,
                nacelle_temp_c = EXCLUDED.nacelle_temp_c,
                pitch_angle_deg = EXCLUDED.pitch_angle_deg,
                status_code = EXCLUDED.status_code,
                is_anomalous = EXCLUDED.is_anomalous,
                ingested_at = EXCLUDED.ingested_at
            """
        )
    )
    conn.execute(text(f"TRUNCATE TABLE {STAGING_TABLE}"))
    return result.rowcount


def load_batch_naive(conn: Connection, readings: list[TransformedReading]) -> int:
    """
    Deliberately naive row-by-row INSERT path, kept ONLY so
    scripts/benchmark.py can demonstrate the throughput delta against
    load_batch_optimized. Never used by the production DAG.
    """
    count = 0
    for r in readings:
        conn.execute(
            text(
                """
                INSERT INTO scada_readings
                    (turbine_id, ts, wind_speed_ms, power_kw, rotor_rpm,
                     nacelle_temp_c, pitch_angle_deg, status_code, is_anomalous, ingested_at)
                VALUES
                    (:turbine_id, :ts, :wind_speed_ms, :power_kw, :rotor_rpm,
                     :nacelle_temp_c, :pitch_angle_deg, :status_code, :is_anomalous, :ingested_at)
                ON CONFLICT (turbine_id, ts) DO UPDATE SET
                    wind_speed_ms = EXCLUDED.wind_speed_ms,
                    power_kw = EXCLUDED.power_kw,
                    rotor_rpm = EXCLUDED.rotor_rpm,
                    nacelle_temp_c = EXCLUDED.nacelle_temp_c,
                    pitch_angle_deg = EXCLUDED.pitch_angle_deg,
                    status_code = EXCLUDED.status_code,
                    is_anomalous = EXCLUDED.is_anomalous,
                    ingested_at = EXCLUDED.ingested_at
                """
            ),
            r.as_dict(),
        )
        count += 1
    return count


def load_rejects(conn: Connection, failed: list[ValidationResult]) -> int:
    if not failed:
        return 0
    now = datetime.now(timezone.utc)
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
                "turbine_id": f.reading.turbine_id,
                "ts": f.reading.ts,
                "raw_payload": str(f.reading.as_dict()),
                "reject_reason": "; ".join(f.reasons),
                "rejected_at": now,
            }
            for f in failed
        ],
    )
    return len(failed)


def update_watermark(conn: Connection, turbine_id: str, new_watermark: datetime) -> None:
    conn.execute(
        text(
            """
            INSERT INTO extraction_watermark (turbine_id, last_extracted_ts)
            VALUES (:turbine_id, :ts)
            ON CONFLICT (turbine_id) DO UPDATE SET last_extracted_ts = EXCLUDED.last_extracted_ts
            WHERE EXCLUDED.last_extracted_ts > extraction_watermark.last_extracted_ts
            """
        ),
        {"turbine_id": turbine_id, "ts": new_watermark},
    )


def record_run_audit(conn: Connection, **kwargs) -> None:
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
        kwargs,
    )
