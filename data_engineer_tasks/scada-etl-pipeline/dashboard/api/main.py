"""
Read-only dashboard API.

Sits directly on top of the same PostgreSQL curated schema the Airflow
pipeline writes to - no separate data store, no caching layer, just SQL
views over `scada_readings` / `pipeline_run_audit` / `scada_readings_rejects`.
Reuses `src.db.session` / `src.config` so connection settings stay identical
to the pipeline's (same env vars, same pooled engine pattern).
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from src.db.session import get_engine

app = FastAPI(title="SCADA Dashboard API")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _rows(query: str, **params) -> list[dict]:
    with get_engine().connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row) for row in result.mappings().all()]


def _row(query: str, **params) -> dict | None:
    rows = _rows(query, **params)
    return rows[0] if rows else None


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/summary")
def summary() -> dict:
    totals = _row(
        """
        SELECT
            (SELECT count(*) FROM scada_readings) AS total_readings,
            (SELECT count(DISTINCT turbine_id) FROM scada_readings) AS total_turbines,
            (SELECT count(*) FROM scada_readings WHERE is_anomalous) AS total_anomalies,
            (SELECT count(*) FROM scada_readings_rejects) AS total_rejects
        """
    )
    fleet_power = _row(
        """
        SELECT round(avg(power_kw), 1) AS avg_power_kw,
               round(avg(wind_speed_ms), 2) AS avg_wind_speed_ms
        FROM (
            SELECT DISTINCT ON (turbine_id) power_kw, wind_speed_ms
            FROM scada_readings
            ORDER BY turbine_id, ts DESC
        ) latest
        """
    )
    last_run = _row(
        """
        SELECT dag_run_id, status, rows_extracted, rows_loaded, rows_rejected,
               duration_seconds, started_at, finished_at
        FROM pipeline_run_audit
        ORDER BY finished_at DESC
        LIMIT 1
        """
    )
    return {**(totals or {}), **(fleet_power or {}), "last_run": last_run}


@app.get("/api/turbines/latest")
def turbines_latest() -> list[dict]:
    return _rows(
        """
        SELECT DISTINCT ON (turbine_id)
            turbine_id, ts, wind_speed_ms, power_kw, rotor_rpm,
            nacelle_temp_c, pitch_angle_deg, status_code, is_anomalous
        FROM scada_readings
        ORDER BY turbine_id, ts DESC
        """
    )


@app.get("/api/turbines/stats")
def turbines_stats() -> list[dict]:
    return _rows(
        """
        SELECT
            turbine_id,
            count(*) AS reading_count,
            round(avg(wind_speed_ms), 2) AS avg_wind_speed_ms,
            round(avg(power_kw), 2) AS avg_power_kw,
            round(max(power_kw), 2) AS max_power_kw,
            sum(CASE WHEN is_anomalous THEN 1 ELSE 0 END) AS anomaly_count
        FROM scada_readings
        GROUP BY turbine_id
        ORDER BY turbine_id
        """
    )


@app.get("/api/turbines/{turbine_id}/timeseries")
def turbine_timeseries(turbine_id: str, limit: int = 200) -> list[dict]:
    if limit < 1 or limit > 2000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 2000")
    rows = _rows(
        """
        SELECT ts, wind_speed_ms, power_kw, rotor_rpm, nacelle_temp_c, is_anomalous
        FROM scada_readings
        WHERE turbine_id = :turbine_id
        ORDER BY ts DESC
        LIMIT :limit
        """,
        turbine_id=turbine_id,
        limit=limit,
    )
    return list(reversed(rows))


@app.get("/api/anomalies")
def anomalies(limit: int = 50) -> list[dict]:
    return _rows(
        """
        SELECT turbine_id, ts, wind_speed_ms, power_kw, rotor_rpm, status_code
        FROM scada_readings
        WHERE is_anomalous
        ORDER BY ts DESC
        LIMIT :limit
        """,
        limit=limit,
    )


@app.get("/api/rejects")
def rejects(limit: int = 50) -> list[dict]:
    return _rows(
        """
        SELECT turbine_id, ts, reject_reason, rejected_at
        FROM scada_readings_rejects
        ORDER BY rejected_at DESC
        LIMIT :limit
        """,
        limit=limit,
    )


@app.get("/api/external")
def external_sources() -> dict:
    weather = _row(
        """
        SELECT source, latitude, longitude, ts, wind_speed_ms, wind_direction_deg,
               temperature_c, pressure_hpa, ingested_at
        FROM weather_api_readings
        ORDER BY ts DESC
        LIMIT 1
        """
    )
    buoy = _row(
        """
        SELECT station_id, ts, wind_speed_ms, wind_gust_ms, wave_height_m,
               air_temp_c, water_temp_c, pressure_hpa, ingested_at
        FROM iot_buoy_readings
        ORDER BY ts DESC
        LIMIT 1
        """
    )
    recent_runs = _rows(
        """
        SELECT dag_run_id, source, status, rows_fetched, rows_loaded, rows_rejected,
               duration_seconds, finished_at
        FROM external_data_run_audit
        ORDER BY finished_at DESC
        LIMIT 10
        """
    )
    return {"weather": weather, "buoy": buoy, "recent_runs": recent_runs}


@app.get("/api/audit/runs")
def audit_runs(limit: int = 20) -> list[dict]:
    return _rows(
        """
        SELECT dag_run_id, status, rows_extracted, rows_loaded, rows_rejected,
               duration_seconds, started_at, finished_at
        FROM pipeline_run_audit
        ORDER BY finished_at DESC
        LIMIT :limit
        """,
        limit=limit,
    )


# Mounted last so it doesn't shadow the /api/* routes above.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
