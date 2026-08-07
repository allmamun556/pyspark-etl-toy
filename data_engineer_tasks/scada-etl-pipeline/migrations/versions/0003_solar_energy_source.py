"""solar energy source: simulated PV plant fleet + real irradiance column

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-07
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Real solar irradiance from Open-Meteo, added to the existing weather
    # source table rather than a new one - it's the same fetch, same row,
    # just one more field pulled from a response we already parse.
    op.add_column(
        "weather_api_readings",
        sa.Column("shortwave_radiation_w_m2", sa.Numeric(6, 1)),
    )

    op.create_table(
        "solar_readings",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("plant_id", sa.String(20), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("irradiance_w_m2", sa.Numeric(6, 2)),
        sa.Column("panel_temp_c", sa.Numeric(5, 2)),
        sa.Column("dc_power_kw", sa.Numeric(8, 2)),
        sa.Column("ac_power_kw", sa.Numeric(8, 2)),
        sa.Column("inverter_efficiency_pct", sa.Numeric(5, 2)),
        sa.Column("status_code", sa.String(20), server_default="operational"),
        sa.Column("is_anomalous", sa.Boolean, server_default=sa.false()),
        sa.Column("ingested_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("plant_id", "ts", name="uq_plant_ts"),
    )
    op.create_index("ix_solar_readings_plant_id", "solar_readings", ["plant_id"])
    op.create_index("ix_solar_readings_ts", "solar_readings", ["ts"])

    op.execute(
        """
        CREATE UNLOGGED TABLE solar_readings_staging (
            plant_id                VARCHAR(20),
            ts                      TIMESTAMPTZ,
            irradiance_w_m2         NUMERIC(6,2),
            panel_temp_c            NUMERIC(5,2),
            dc_power_kw             NUMERIC(8,2),
            ac_power_kw             NUMERIC(8,2),
            inverter_efficiency_pct NUMERIC(5,2),
            status_code             VARCHAR(20),
            is_anomalous            BOOLEAN,
            ingested_at             TIMESTAMPTZ
        )
        """
    )

    op.create_table(
        "solar_readings_rejects",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("plant_id", sa.String(20)),
        sa.Column("ts", sa.DateTime(timezone=True)),
        sa.Column("raw_payload", sa.Text),
        sa.Column("reject_reason", sa.Text),
        sa.Column("rejected_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "solar_extraction_watermark",
        sa.Column("plant_id", sa.String(20), primary_key=True),
        sa.Column("last_extracted_ts", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("solar_extraction_watermark")
    op.drop_table("solar_readings_rejects")
    op.execute("DROP TABLE solar_readings_staging")
    op.drop_index("ix_solar_readings_ts", table_name="solar_readings")
    op.drop_index("ix_solar_readings_plant_id", table_name="solar_readings")
    op.drop_table("solar_readings")
    op.drop_column("weather_api_readings", "shortwave_radiation_w_m2")
