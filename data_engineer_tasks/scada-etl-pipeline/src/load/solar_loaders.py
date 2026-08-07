"""
Load layer for the solar plant fleet. Same COPY + staged-UPSERT pattern as
loaders.py. `record_run_audit` isn't duplicated here - pipeline_run_audit's
shape (rows_extracted/loaded/rejected, duration, status) fits the solar DAG
exactly as-is, distinguished by task_id, so the solar DAG imports that
function directly from src.load.loaders instead of a copy living here.
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.transform.solar_transformers import TransformedSolarReading
from src.validation.solar_validators import SolarValidationResult

STAGING_TABLE = "solar_readings_staging"


def _reading_to_csv_row(r: TransformedSolarReading) -> list:
    return [
        r.plant_id,
        r.ts.isoformat(),
        r.irradiance_w_m2,
        r.panel_temp_c,
        r.dc_power_kw,
        r.ac_power_kw,
        r.inverter_efficiency_pct,
        r.status_code,
        r.is_anomalous,
        r.ingested_at.isoformat(),
    ]


def load_solar_batch_optimized(conn: Connection, readings: list[TransformedSolarReading]) -> int:
    """Batch-load via COPY + staged UPSERT. Returns rows written to the curated table."""
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
            (plant_id, ts, irradiance_w_m2, panel_temp_c, dc_power_kw,
             ac_power_kw, inverter_efficiency_pct, status_code, is_anomalous, ingested_at)
        FROM STDIN WITH (FORMAT csv)
        """,
        buf,
    )

    result = conn.execute(
        text(
            f"""
            INSERT INTO solar_readings
                (plant_id, ts, irradiance_w_m2, panel_temp_c, dc_power_kw,
                 ac_power_kw, inverter_efficiency_pct, status_code, is_anomalous, ingested_at)
            SELECT plant_id, ts, irradiance_w_m2, panel_temp_c, dc_power_kw,
                   ac_power_kw, inverter_efficiency_pct, status_code, is_anomalous, ingested_at
            FROM {STAGING_TABLE}
            ON CONFLICT (plant_id, ts) DO UPDATE SET
                irradiance_w_m2 = EXCLUDED.irradiance_w_m2,
                panel_temp_c = EXCLUDED.panel_temp_c,
                dc_power_kw = EXCLUDED.dc_power_kw,
                ac_power_kw = EXCLUDED.ac_power_kw,
                inverter_efficiency_pct = EXCLUDED.inverter_efficiency_pct,
                status_code = EXCLUDED.status_code,
                is_anomalous = EXCLUDED.is_anomalous,
                ingested_at = EXCLUDED.ingested_at
            """
        )
    )
    conn.execute(text(f"TRUNCATE TABLE {STAGING_TABLE}"))
    return result.rowcount


def load_solar_rejects(conn: Connection, failed: list[SolarValidationResult]) -> int:
    if not failed:
        return 0
    now = datetime.now(timezone.utc)
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
                "plant_id": f.reading.plant_id,
                "ts": f.reading.ts,
                "raw_payload": str(f.reading.as_dict()),
                "reject_reason": "; ".join(f.reasons),
                "rejected_at": now,
            }
            for f in failed
        ],
    )
    return len(failed)


def update_solar_watermark(conn: Connection, plant_id: str, new_watermark: datetime) -> None:
    conn.execute(
        text(
            """
            INSERT INTO solar_extraction_watermark (plant_id, last_extracted_ts)
            VALUES (:plant_id, :ts)
            ON CONFLICT (plant_id) DO UPDATE SET last_extracted_ts = EXCLUDED.last_extracted_ts
            WHERE EXCLUDED.last_extracted_ts > solar_extraction_watermark.last_extracted_ts
            """
        ),
        {"plant_id": plant_id, "ts": new_watermark},
    )
