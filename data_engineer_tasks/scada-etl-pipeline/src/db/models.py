"""
ORM models for the curated schema. Kept minimal and mirrors sql/init.sql /
the Alembic migration exactly — the migration is the source of truth for
what's actually deployed; these models are used for read/write access and
for the (rare) case where we build queries with the ORM rather than raw SQL.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ScadaReading(Base):
    __tablename__ = "scada_readings"
    __table_args__ = (UniqueConstraint("turbine_id", "ts", name="uq_turbine_ts"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    turbine_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    wind_speed_ms: Mapped[float] = mapped_column(Numeric(6, 2))
    power_kw: Mapped[float] = mapped_column(Numeric(8, 2))
    rotor_rpm: Mapped[float] = mapped_column(Numeric(5, 2))
    nacelle_temp_c: Mapped[float] = mapped_column(Numeric(5, 2))
    pitch_angle_deg: Mapped[float] = mapped_column(Numeric(5, 2))
    status_code: Mapped[str] = mapped_column(String(20), default="operational")
    is_anomalous: Mapped[bool] = mapped_column(Boolean, default=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ScadaReadingReject(Base):
    __tablename__ = "scada_readings_rejects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    turbine_id: Mapped[str] = mapped_column(String(20))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_payload: Mapped[str] = mapped_column(Text)
    reject_reason: Mapped[str] = mapped_column(Text)
    rejected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExtractionWatermark(Base):
    __tablename__ = "extraction_watermark"

    turbine_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    last_extracted_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WeatherApiReading(Base):
    """Real ambient weather pulled from the Open-Meteo HTTP API (no key required)."""

    __tablename__ = "weather_api_readings"
    __table_args__ = (UniqueConstraint("latitude", "longitude", "ts", name="uq_weather_loc_ts"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(30), default="open-meteo")
    latitude: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    wind_speed_ms: Mapped[float] = mapped_column(Numeric(6, 2))
    wind_direction_deg: Mapped[float] = mapped_column(Numeric(5, 1))
    temperature_c: Mapped[float] = mapped_column(Numeric(5, 2))
    pressure_hpa: Mapped[float] = mapped_column(Numeric(7, 2))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IotBuoyReading(Base):
    """Real IoT sensor telemetry from a NOAA NDBC ocean buoy (no key required)."""

    __tablename__ = "iot_buoy_readings"
    __table_args__ = (UniqueConstraint("station_id", "ts", name="uq_buoy_station_ts"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    wind_speed_ms: Mapped[float] = mapped_column(Numeric(6, 2))
    wind_gust_ms: Mapped[float] = mapped_column(Numeric(6, 2))
    wave_height_m: Mapped[float] = mapped_column(Numeric(5, 2))
    air_temp_c: Mapped[float] = mapped_column(Numeric(5, 2))
    water_temp_c: Mapped[float] = mapped_column(Numeric(5, 2))
    pressure_hpa: Mapped[float] = mapped_column(Numeric(7, 2))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExternalDataRunAudit(Base):
    """Audit trail for the external_data_sources DAG, mirrors pipeline_run_audit."""

    __tablename__ = "external_data_run_audit"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dag_run_id: Mapped[str] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(30))
    rows_fetched: Mapped[int] = mapped_column(default=0)
    rows_loaded: Mapped[int] = mapped_column(default=0)
    rows_rejected: Mapped[int] = mapped_column(default=0)
    duration_seconds: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PipelineRunAudit(Base):
    __tablename__ = "pipeline_run_audit"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dag_run_id: Mapped[str] = mapped_column(String(100))
    task_id: Mapped[str] = mapped_column(String(100))
    rows_extracted: Mapped[int] = mapped_column(default=0)
    rows_loaded: Mapped[int] = mapped_column(default=0)
    rows_rejected: Mapped[int] = mapped_column(default=0)
    duration_seconds: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
