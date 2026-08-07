"""timescaledb hypertables + retention policy for the two high-volume
readings tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-07

Only scada_readings and solar_readings become hypertables - they're the
two tables with genuine time-series volume (a reading every 5 min per
asset). weather_api_readings/iot_buoy_readings get one row per 15-minute
fetch; hypertable chunking exists to solve a problem those tables don't
have, so they stay plain tables.

Requires the postgres image to actually ship the timescaledb extension
(see docker-compose.yml - postgres:16-alpine was swapped for
timescale/timescaledb, a drop-in-compatible build on the same PostgreSQL
16 with the extension pre-installed).
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

RETENTION_INTERVAL = "90 days"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    for table in ("scada_readings", "solar_readings"):
        # TimescaleDB requires every unique index/primary key on a
        # hypertable to include the partitioning column. The existing
        # `id`-only primary key doesn't, so it's replaced with a composite
        # (id, ts) key - id (the bigserial) still makes each row uniquely
        # identifiable, `ts` just has to ride along on the same
        # constraint. Nothing in this codebase looks up a row by `id`
        # alone (checked before writing this migration), so this is safe.
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {table}_pkey")
        op.execute(f"ALTER TABLE {table} ADD PRIMARY KEY (id, ts)")

        op.execute(
            f"SELECT create_hypertable('{table}', 'ts', "
            f"if_not_exists => TRUE, migrate_data => TRUE)"
        )

        # Automatically drops chunks entirely older than the retention
        # window on TimescaleDB's own background schedule - the "unbounded
        # table growth" problem this pipeline had no answer for before.
        op.execute(
            f"SELECT add_retention_policy('{table}', INTERVAL '{RETENTION_INTERVAL}')"
        )


def downgrade() -> None:
    for table in ("scada_readings", "solar_readings"):
        op.execute(f"SELECT remove_retention_policy('{table}', if_exists => TRUE)")
        # TimescaleDB doesn't support "un-hypertable-ing" a table in place;
        # downgrading this migration only removes the retention policy and
        # restores the original single-column primary key. Full reversal
        # to a plain table would mean recreating it from the hypertable's
        # data, which - given migrate_data => TRUE already made this a
        # one-way trip for chunked storage - isn't attempted here.
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {table}_pkey")
        op.execute(f"ALTER TABLE {table} ADD PRIMARY KEY (id)")
