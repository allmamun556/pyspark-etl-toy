"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scada_readings",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("turbine_id", sa.String(20), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wind_speed_ms", sa.Numeric(6, 2)),
        sa.Column("power_kw", sa.Numeric(8, 2)),
        sa.Column("rotor_rpm", sa.Numeric(5, 2)),
        sa.Column("nacelle_temp_c", sa.Numeric(5, 2)),
        sa.Column("pitch_angle_deg", sa.Numeric(5, 2)),
        sa.Column("status_code", sa.String(20), server_default="operational"),
        sa.Column("is_anomalous", sa.Boolean, server_default=sa.false()),
        sa.Column("ingested_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("turbine_id", "ts", name="uq_turbine_ts"),
    )
    op.create_index("ix_scada_readings_turbine_id", "scada_readings", ["turbine_id"])
    op.create_index("ix_scada_readings_ts", "scada_readings", ["ts"])

    op.execute(
        """
        CREATE UNLOGGED TABLE scada_readings_staging (
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
        )
        """
    )

    op.create_table(
        "scada_readings_rejects",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("turbine_id", sa.String(20)),
        sa.Column("ts", sa.DateTime(timezone=True)),
        sa.Column("raw_payload", sa.Text),
        sa.Column("reject_reason", sa.Text),
        sa.Column("rejected_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "extraction_watermark",
        sa.Column("turbine_id", sa.String(20), primary_key=True),
        sa.Column("last_extracted_ts", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "pipeline_run_audit",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("dag_run_id", sa.String(100)),
        sa.Column("task_id", sa.String(100)),
        sa.Column("rows_extracted", sa.Integer, server_default="0"),
        sa.Column("rows_loaded", sa.Integer, server_default="0"),
        sa.Column("rows_rejected", sa.Integer, server_default="0"),
        sa.Column("duration_seconds", sa.Numeric(10, 3), server_default="0"),
        sa.Column("status", sa.String(20)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("pipeline_run_audit")
    op.drop_table("extraction_watermark")
    op.drop_table("scada_readings_rejects")
    op.execute("DROP TABLE scada_readings_staging")
    op.drop_index("ix_scada_readings_ts", table_name="scada_readings")
    op.drop_index("ix_scada_readings_turbine_id", table_name="scada_readings")
    op.drop_table("scada_readings")
