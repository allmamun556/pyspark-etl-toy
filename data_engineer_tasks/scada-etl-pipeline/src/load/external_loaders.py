"""
Load layer for the external (weather API / IoT buoy) sources. One row per
fetch, so this is a plain idempotent UPSERT rather than the batch COPY path
in src/load/loaders.py - there's no throughput problem to solve at this
volume.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.extract.iot_buoy_extractor import BuoyReading
from src.extract.weather_api_extractor import WeatherReading


def load_weather_reading(conn: Connection, reading: WeatherReading, ingested_at: datetime) -> None:
    conn.execute(
        text(
            """
            INSERT INTO weather_api_readings
                (source, latitude, longitude, ts, wind_speed_ms,
                 wind_direction_deg, temperature_c, pressure_hpa,
                 shortwave_radiation_w_m2, ingested_at)
            VALUES
                (:source, :latitude, :longitude, :ts, :wind_speed_ms,
                 :wind_direction_deg, :temperature_c, :pressure_hpa,
                 :shortwave_radiation_w_m2, :ingested_at)
            ON CONFLICT (latitude, longitude, ts) DO UPDATE SET
                wind_speed_ms = EXCLUDED.wind_speed_ms,
                wind_direction_deg = EXCLUDED.wind_direction_deg,
                temperature_c = EXCLUDED.temperature_c,
                pressure_hpa = EXCLUDED.pressure_hpa,
                shortwave_radiation_w_m2 = EXCLUDED.shortwave_radiation_w_m2,
                ingested_at = EXCLUDED.ingested_at
            """
        ),
        {
            "source": reading.source,
            "latitude": reading.latitude,
            "longitude": reading.longitude,
            "ts": reading.ts,
            "wind_speed_ms": reading.wind_speed_ms,
            "wind_direction_deg": reading.wind_direction_deg,
            "temperature_c": reading.temperature_c,
            "pressure_hpa": reading.pressure_hpa,
            "shortwave_radiation_w_m2": reading.shortwave_radiation_w_m2,
            "ingested_at": ingested_at,
        },
    )


def load_buoy_reading(conn: Connection, reading: BuoyReading, ingested_at: datetime) -> None:
    conn.execute(
        text(
            """
            INSERT INTO iot_buoy_readings
                (station_id, ts, wind_speed_ms, wind_gust_ms, wave_height_m,
                 air_temp_c, water_temp_c, pressure_hpa, ingested_at)
            VALUES
                (:station_id, :ts, :wind_speed_ms, :wind_gust_ms, :wave_height_m,
                 :air_temp_c, :water_temp_c, :pressure_hpa, :ingested_at)
            ON CONFLICT (station_id, ts) DO UPDATE SET
                wind_speed_ms = EXCLUDED.wind_speed_ms,
                wind_gust_ms = EXCLUDED.wind_gust_ms,
                wave_height_m = EXCLUDED.wave_height_m,
                air_temp_c = EXCLUDED.air_temp_c,
                water_temp_c = EXCLUDED.water_temp_c,
                pressure_hpa = EXCLUDED.pressure_hpa,
                ingested_at = EXCLUDED.ingested_at
            """
        ),
        {
            "station_id": reading.station_id,
            "ts": reading.ts,
            "wind_speed_ms": reading.wind_speed_ms,
            "wind_gust_ms": reading.wind_gust_ms,
            "wave_height_m": reading.wave_height_m,
            "air_temp_c": reading.air_temp_c,
            "water_temp_c": reading.water_temp_c,
            "pressure_hpa": reading.pressure_hpa,
            "ingested_at": ingested_at,
        },
    )


def record_external_run_audit(conn: Connection, **kwargs) -> None:
    conn.execute(
        text(
            """
            INSERT INTO external_data_run_audit
                (dag_run_id, source, rows_fetched, rows_loaded, rows_rejected,
                 duration_seconds, status, started_at, finished_at)
            VALUES
                (:dag_run_id, :source, :rows_fetched, :rows_loaded, :rows_rejected,
                 :duration_seconds, :status, :started_at, :finished_at)
            """
        ),
        kwargs,
    )
