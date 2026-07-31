"""external data sources: weather API + IoT buoy

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weather_api_readings",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(30), server_default="open-meteo"),
        sa.Column("latitude", sa.Numeric(6, 3), nullable=False),
        sa.Column("longitude", sa.Numeric(6, 3), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wind_speed_ms", sa.Numeric(6, 2)),
        sa.Column("wind_direction_deg", sa.Numeric(5, 1)),
        sa.Column("temperature_c", sa.Numeric(5, 2)),
        sa.Column("pressure_hpa", sa.Numeric(7, 2)),
        sa.Column("ingested_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("latitude", "longitude", "ts", name="uq_weather_loc_ts"),
    )
    op.create_index("ix_weather_api_readings_ts", "weather_api_readings", ["ts"])

    op.create_table(
        "iot_buoy_readings",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("station_id", sa.String(20), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wind_speed_ms", sa.Numeric(6, 2)),
        sa.Column("wind_gust_ms", sa.Numeric(6, 2)),
        sa.Column("wave_height_m", sa.Numeric(5, 2)),
        sa.Column("air_temp_c", sa.Numeric(5, 2)),
        sa.Column("water_temp_c", sa.Numeric(5, 2)),
        sa.Column("pressure_hpa", sa.Numeric(7, 2)),
        sa.Column("ingested_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("station_id", "ts", name="uq_buoy_station_ts"),
    )
    op.create_index("ix_iot_buoy_readings_station_id", "iot_buoy_readings", ["station_id"])
    op.create_index("ix_iot_buoy_readings_ts", "iot_buoy_readings", ["ts"])

    op.create_table(
        "external_data_run_audit",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("dag_run_id", sa.String(100)),
        sa.Column("source", sa.String(30)),
        sa.Column("rows_fetched", sa.Integer, server_default="0"),
        sa.Column("rows_loaded", sa.Integer, server_default="0"),
        sa.Column("rows_rejected", sa.Integer, server_default="0"),
        sa.Column("duration_seconds", sa.Numeric(10, 3), server_default="0"),
        sa.Column("status", sa.String(20)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("external_data_run_audit")
    op.drop_index("ix_iot_buoy_readings_ts", table_name="iot_buoy_readings")
    op.drop_index("ix_iot_buoy_readings_station_id", table_name="iot_buoy_readings")
    op.drop_table("iot_buoy_readings")
    op.drop_index("ix_weather_api_readings_ts", table_name="weather_api_readings")
    op.drop_table("weather_api_readings")
