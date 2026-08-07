"""
Verifies, against a real database, the idempotency claim this project makes
repeatedly in its docs: replaying a load (e.g. an Airflow retry re-running
a task, or two overlapping windows sharing rows) converges to the same
curated rows instead of duplicating them. That claim rests on
`ON CONFLICT (turbine_id, ts) DO UPDATE` in load_batch_optimized() - this
script is the thing that actually exercises it against Postgres, rather
than leaving it as an assertion about the SQL's design.

Two scenarios:
  1. Replay: load the exact same batch twice. Row count must not grow.
  2. Overlap: load batch A, then batch B whose keys partially overlap A's.
     Final row count must equal the UNION of keys, not len(A) + len(B).

Usage:
    python scripts/verify_idempotency.py

Requires a running Postgres instance reachable via the settings in .env
(e.g. `docker compose up -d postgres`), same as scripts/benchmark.py.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from src.db.session import get_engine  # noqa: E402
from src.load.loaders import load_batch_optimized  # noqa: E402
from src.transform.transformers import TransformedReading  # noqa: E402

MARKER_PREFIX = "IDEM-"
BASE_TS = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _reading(turbine_suffix: str, minute_offset: int, power_kw: float) -> TransformedReading:
    now = datetime.now(timezone.utc)
    return TransformedReading(
        turbine_id=f"{MARKER_PREFIX}{turbine_suffix}",
        ts=BASE_TS + timedelta(minutes=minute_offset),
        wind_speed_ms=7.5,
        power_kw=power_kw,
        rotor_rpm=12.0,
        nacelle_temp_c=35.0,
        pitch_angle_deg=2.0,
        status_code="operational",
        is_anomalous=False,
        ingested_at=now,
    )


def cleanup(conn) -> None:
    conn.execute(
        text("DELETE FROM scada_readings WHERE turbine_id LIKE :prefix"),
        {"prefix": f"{MARKER_PREFIX}%"},
    )


def count_marker_rows(conn) -> int:
    return conn.execute(
        text("SELECT count(*) FROM scada_readings WHERE turbine_id LIKE :prefix"),
        {"prefix": f"{MARKER_PREFIX}%"},
    ).scalar_one()


def verify_replay(engine) -> None:
    print("--- Scenario 1: replay the same batch twice ---")
    batch = [_reading("001", i, 1500.0) for i in range(50)]

    with engine.begin() as conn:
        load_batch_optimized(conn, batch)
        after_first = count_marker_rows(conn)

    with engine.begin() as conn:
        load_batch_optimized(conn, batch)
        after_second = count_marker_rows(conn)

    print(f"  rows after 1st load: {after_first}, after replay: {after_second}")
    assert after_first == len(batch), (
        f"expected {len(batch)} rows after the first load, got {after_first}"
    )
    assert after_second == after_first, (
        f"replaying the identical batch changed row count "
        f"({after_first} -> {after_second}) - upsert is not idempotent"
    )
    print("  PASS")


def verify_overlap(engine) -> None:
    print("--- Scenario 2: overlapping batches (simulated concurrent windows) ---")
    batch_a = [_reading("002", i, 1500.0) for i in range(0, 30)]  # minutes 0-29
    batch_b = [_reading("002", i, 1600.0) for i in range(20, 50)]  # minutes 20-49
    expected_union_size = 50  # minutes 0-49, deduplicated on (turbine_id, ts)

    with engine.begin() as conn:
        load_batch_optimized(conn, batch_a)

    with engine.begin() as conn:
        load_batch_optimized(conn, batch_b)
        final_count = count_marker_rows(conn) - 50  # subtract scenario 1's 50 rows

    print(f"  rows after overlapping loads: {final_count} (expected {expected_union_size})")
    assert final_count == expected_union_size, (
        f"expected {expected_union_size} deduplicated rows from overlapping "
        f"batches, got {final_count} - overlapping windows are duplicating rows"
    )
    print("  PASS")


def main() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        cleanup(conn)
    try:
        verify_replay(engine)
        verify_overlap(engine)
    finally:
        with engine.begin() as conn:
            cleanup(conn)
    print("\nAll idempotency checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
