-- Bootstrap schema. In practice this is applied via Alembic
-- (migrations/versions/0001_initial_schema.py); this file exists as a
-- human-readable reference and for quick local `psql -f` setup.

CREATE TABLE IF NOT EXISTS scada_readings (
    id              BIGSERIAL PRIMARY KEY,
    turbine_id      VARCHAR(20)  NOT NULL,
    ts              TIMESTAMPTZ  NOT NULL,
    wind_speed_ms   NUMERIC(6,2),
    power_kw        NUMERIC(8,2),
    rotor_rpm       NUMERIC(5,2),
    nacelle_temp_c  NUMERIC(5,2),
    pitch_angle_deg NUMERIC(5,2),
    status_code     VARCHAR(20) DEFAULT 'operational',
    is_anomalous    BOOLEAN     DEFAULT FALSE,
    ingested_at     TIMESTAMPTZ,
    CONSTRAINT uq_turbine_ts UNIQUE (turbine_id, ts)
);
CREATE INDEX IF NOT EXISTS ix_scada_readings_turbine_id ON scada_readings (turbine_id);
CREATE INDEX IF NOT EXISTS ix_scada_readings_ts ON scada_readings (ts);

CREATE UNLOGGED TABLE IF NOT EXISTS scada_readings_staging (
    turbine_id      VARCHAR(20),
    ts              TIMESTAMPTZ,
    wind_speed_ms   NUMERIC(6,2),
    power_kw        NUMERIC(8,2),
    rotor_rpm       NUMERIC(5,2),
    nacelle_temp_c  NUMERIC(5,2),
    pitch_angle_deg NUMERIC(5,2),
    status_code     VARCHAR(20),
    is_anomalous    BOOLEAN,
    ingested_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS scada_readings_rejects (
    id              BIGSERIAL PRIMARY KEY,
    turbine_id      VARCHAR(20),
    ts              TIMESTAMPTZ,
    raw_payload     TEXT,
    reject_reason   TEXT,
    rejected_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS extraction_watermark (
    turbine_id        VARCHAR(20) PRIMARY KEY,
    last_extracted_ts TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_run_audit (
    id                BIGSERIAL PRIMARY KEY,
    dag_run_id        VARCHAR(100),
    task_id           VARCHAR(100),
    rows_extracted    INTEGER DEFAULT 0,
    rows_loaded       INTEGER DEFAULT 0,
    rows_rejected     INTEGER DEFAULT 0,
    duration_seconds  NUMERIC(10,3) DEFAULT 0,
    status            VARCHAR(20),
    started_at        TIMESTAMPTZ,
    finished_at       TIMESTAMPTZ
);

-- External sources: real HTTP weather API (Open-Meteo) + real IoT ocean
-- buoy (NOAA NDBC). See migrations/versions/0002_external_data_sources.py.
CREATE TABLE IF NOT EXISTS weather_api_readings (
    id                 BIGSERIAL PRIMARY KEY,
    source             VARCHAR(30) DEFAULT 'open-meteo',
    latitude           NUMERIC(6,3)  NOT NULL,
    longitude          NUMERIC(6,3)  NOT NULL,
    ts                 TIMESTAMPTZ   NOT NULL,
    wind_speed_ms      NUMERIC(6,2),
    wind_direction_deg NUMERIC(5,1),
    temperature_c      NUMERIC(5,2),
    pressure_hpa       NUMERIC(7,2),
    ingested_at        TIMESTAMPTZ,
    CONSTRAINT uq_weather_loc_ts UNIQUE (latitude, longitude, ts)
);
CREATE INDEX IF NOT EXISTS ix_weather_api_readings_ts ON weather_api_readings (ts);

CREATE TABLE IF NOT EXISTS iot_buoy_readings (
    id             BIGSERIAL PRIMARY KEY,
    station_id     VARCHAR(20)  NOT NULL,
    ts             TIMESTAMPTZ  NOT NULL,
    wind_speed_ms  NUMERIC(6,2),
    wind_gust_ms   NUMERIC(6,2),
    wave_height_m  NUMERIC(5,2),
    air_temp_c     NUMERIC(5,2),
    water_temp_c   NUMERIC(5,2),
    pressure_hpa   NUMERIC(7,2),
    ingested_at    TIMESTAMPTZ,
    CONSTRAINT uq_buoy_station_ts UNIQUE (station_id, ts)
);
CREATE INDEX IF NOT EXISTS ix_iot_buoy_readings_station_id ON iot_buoy_readings (station_id);
CREATE INDEX IF NOT EXISTS ix_iot_buoy_readings_ts ON iot_buoy_readings (ts);

CREATE TABLE IF NOT EXISTS external_data_run_audit (
    id                BIGSERIAL PRIMARY KEY,
    dag_run_id        VARCHAR(100),
    source            VARCHAR(30),
    rows_fetched      INTEGER DEFAULT 0,
    rows_loaded       INTEGER DEFAULT 0,
    rows_rejected     INTEGER DEFAULT 0,
    duration_seconds  NUMERIC(10,3) DEFAULT 0,
    status            VARCHAR(20),
    started_at        TIMESTAMPTZ,
    finished_at       TIMESTAMPTZ
);
