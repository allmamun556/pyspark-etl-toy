"""
Read-only dashboard API.

Sits directly on top of the same PostgreSQL curated schema the Airflow
pipelines write to - no separate data store, no caching layer, just SQL
views over `scada_readings` / `solar_readings` / `pipeline_run_audit` /
their reject tables. Reuses `src.db.session` / `src.config` so connection
settings stay identical to the pipelines' (same env vars, same pooled
engine pattern).
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
    # Reads dbt's turbine_daily_summary mart (rolled up across all its
    # days) rather than re-aggregating scada_readings directly - the two
    # used to compute "average power per turbine" via two independently
    # maintained SQL statements, which is exactly how the same metric
    # quietly drifts between a dashboard and a data-team's model. Weighted
    # by each day's reading_count so a day with fewer readings doesn't
    # count as heavily as a full one.
    return _rows(
        """
        SELECT
            turbine_id,
            sum(reading_count) AS reading_count,
            round(
                sum(avg_wind_speed_ms * reading_count) / sum(reading_count), 2
            ) AS avg_wind_speed_ms,
            round(sum(avg_power_kw * reading_count) / sum(reading_count), 2) AS avg_power_kw,
            round(max(max_power_kw), 2) AS max_power_kw,
            sum(anomaly_count) AS anomaly_count
        FROM marts.turbine_daily_summary
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


@app.get("/api/solar/summary")
def solar_summary() -> dict:
    totals = _row(
        """
        SELECT
            (SELECT count(*) FROM solar_readings) AS total_readings,
            (SELECT count(DISTINCT plant_id) FROM solar_readings) AS total_plants,
            (SELECT count(*) FROM solar_readings WHERE is_anomalous) AS total_anomalies,
            (SELECT count(*) FROM solar_readings_rejects) AS total_rejects
        """
    )
    fleet_power = _row(
        """
        SELECT round(avg(dc_power_kw), 1) AS avg_dc_power_kw,
               round(avg(ac_power_kw), 1) AS avg_ac_power_kw,
               round(avg(irradiance_w_m2), 1) AS avg_irradiance_w_m2
        FROM (
            SELECT DISTINCT ON (plant_id) dc_power_kw, ac_power_kw, irradiance_w_m2
            FROM solar_readings
            ORDER BY plant_id, ts DESC
        ) latest
        """
    )
    last_run = _row(
        """
        SELECT dag_run_id, status, rows_extracted, rows_loaded, rows_rejected,
               duration_seconds, started_at, finished_at
        FROM pipeline_run_audit
        WHERE task_id = 'solar_etl_pipeline'
        ORDER BY finished_at DESC
        LIMIT 1
        """
    )
    return {**(totals or {}), **(fleet_power or {}), "last_run": last_run}


@app.get("/api/solar/plants/latest")
def solar_plants_latest() -> list[dict]:
    return _rows(
        """
        SELECT DISTINCT ON (plant_id)
            plant_id, ts, irradiance_w_m2, panel_temp_c, dc_power_kw,
            ac_power_kw, inverter_efficiency_pct, status_code, is_anomalous
        FROM solar_readings
        ORDER BY plant_id, ts DESC
        """
    )


@app.get("/api/solar/plants/stats")
def solar_plants_stats() -> list[dict]:
    # Same reasoning as /api/turbines/stats: reads dbt's solar_daily_summary
    # mart instead of duplicating the aggregation over solar_readings.
    return _rows(
        """
        SELECT
            plant_id,
            sum(reading_count) AS reading_count,
            round(
                sum(avg_irradiance_w_m2 * reading_count) / sum(reading_count), 2
            ) AS avg_irradiance_w_m2,
            round(sum(avg_dc_power_kw * reading_count) / sum(reading_count), 2) AS avg_dc_power_kw,
            round(max(max_ac_power_kw), 2) AS max_ac_power_kw,
            sum(anomaly_count) AS anomaly_count
        FROM marts.solar_daily_summary
        GROUP BY plant_id
        ORDER BY plant_id
        """
    )


@app.get("/api/solar/plants/{plant_id}/timeseries")
def solar_plant_timeseries(plant_id: str, limit: int = 200) -> list[dict]:
    if limit < 1 or limit > 2000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 2000")
    rows = _rows(
        """
        SELECT ts, irradiance_w_m2, dc_power_kw, ac_power_kw, panel_temp_c, is_anomalous
        FROM solar_readings
        WHERE plant_id = :plant_id
        ORDER BY ts DESC
        LIMIT :limit
        """,
        plant_id=plant_id,
        limit=limit,
    )
    return list(reversed(rows))


@app.get("/api/solar/anomalies")
def solar_anomalies(limit: int = 50) -> list[dict]:
    return _rows(
        """
        SELECT plant_id, ts, irradiance_w_m2, dc_power_kw, ac_power_kw, status_code
        FROM solar_readings
        WHERE is_anomalous
        ORDER BY ts DESC
        LIMIT :limit
        """,
        limit=limit,
    )


@app.get("/api/solar/rejects")
def solar_rejects(limit: int = 50) -> list[dict]:
    return _rows(
        """
        SELECT plant_id, ts, reject_reason, rejected_at
        FROM solar_readings_rejects
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
               temperature_c, pressure_hpa, shortwave_radiation_w_m2, ingested_at
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
def audit_runs(limit: int = 20, task_id: str | None = None) -> list[dict]:
    # task_id doubles as the pipeline name here (scada_etl_pipeline vs
    # solar_etl_pipeline) - both DAGs share this table. Filtering server-side
    # (rather than fetching N mixed rows and filtering in the browser) is
    # what keeps each fleet's dashboard page showing a full, correctly
    # bounded list of its own runs instead of an under-filled one.
    if task_id is not None:
        return _rows(
            """
            SELECT task_id, dag_run_id, status, rows_extracted, rows_loaded, rows_rejected,
                   duration_seconds, started_at, finished_at
            FROM pipeline_run_audit
            WHERE task_id = :task_id
            ORDER BY finished_at DESC
            LIMIT :limit
            """,
            limit=limit,
            task_id=task_id,
        )
    return _rows(
        """
        SELECT task_id, dag_run_id, status, rows_extracted, rows_loaded, rows_rejected,
               duration_seconds, started_at, finished_at
        FROM pipeline_run_audit
        ORDER BY finished_at DESC
        LIMIT :limit
        """,
        limit=limit,
    )


# Mounted last so it doesn't shadow the /api/* routes above.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
