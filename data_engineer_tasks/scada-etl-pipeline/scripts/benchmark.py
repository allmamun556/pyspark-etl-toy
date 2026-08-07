"""
Benchmark: naive row-by-row INSERT vs the optimized COPY+staged-UPSERT path.

This is what turns "improved pipeline efficiency by 40%" from a claim into a
number you can reproduce and defend in an interview.

Usage:
    python scripts/benchmark.py --rows 500000
    python scripts/benchmark.py --rows 500000 --skip-naive   # optimized path only, for huge N

Requires a running Postgres instance reachable via the settings in .env
(e.g. `docker compose up -d postgres`).
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from src.db.session import get_engine  # noqa: E402
from src.load.loaders import load_batch_naive, load_batch_optimized  # noqa: E402
from src.transform.transformers import TransformedReading  # noqa: E402


def make_synthetic_readings(n: int, turbine_prefix: str) -> list[TransformedReading]:
    base_ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rng = random.Random(42)
    readings = []
    for i in range(n):
        readings.append(
            TransformedReading(
                turbine_id=f"{turbine_prefix}-{i % 50:03d}",
                ts=base_ts + timedelta(seconds=i * 10),
                wind_speed_ms=round(rng.uniform(0, 25), 2),
                power_kw=round(rng.uniform(0, 3300), 2),
                rotor_rpm=round(rng.uniform(0, 18), 2),
                nacelle_temp_c=round(rng.uniform(-10, 40), 2),
                pitch_angle_deg=round(rng.uniform(0, 30), 2),
                status_code="operational",
                is_anomalous=False,
                ingested_at=datetime.now(timezone.utc),
            )
        )
    return readings


def ensure_schema(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS scada_readings (
                    id BIGSERIAL PRIMARY KEY,
                    turbine_id VARCHAR(20) NOT NULL,
                    ts TIMESTAMPTZ NOT NULL,
                    wind_speed_ms NUMERIC(6,2),
                    power_kw NUMERIC(8,2),
                    rotor_rpm NUMERIC(5,2),
                    nacelle_temp_c NUMERIC(5,2),
                    pitch_angle_deg NUMERIC(5,2),
                    status_code VARCHAR(20) DEFAULT 'operational',
                    is_anomalous BOOLEAN DEFAULT FALSE,
                    ingested_at TIMESTAMPTZ,
                    CONSTRAINT uq_turbine_ts UNIQUE (turbine_id, ts)
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE UNLOGGED TABLE IF NOT EXISTS scada_readings_staging (
                    turbine_id VARCHAR(20), ts TIMESTAMPTZ, wind_speed_ms NUMERIC(6,2),
                    power_kw NUMERIC(8,2), rotor_rpm NUMERIC(5,2), nacelle_temp_c NUMERIC(5,2),
                    pitch_angle_deg NUMERIC(5,2), status_code VARCHAR(20),
                    is_anomalous BOOLEAN, ingested_at TIMESTAMPTZ
                )
                """
            )
        )


def cleanup_benchmark_rows(engine) -> None:
    """
    Deletes every OPT-/NAIVE- row this script could have written. Called
    both before a run (in case a previous run crashed mid-benchmark) and
    always after (via try/finally in main()) - this table is also the
    pipeline's real curated table, and leaving synthetic rows in it after
    the script exits has previously caused it to be miscounted as real
    pipeline data on the dashboard.
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                "DELETE FROM scada_readings "
                "WHERE turbine_id LIKE 'OPT-%' OR turbine_id LIKE 'NAIVE-%'"
            )
        )


def run_naive(engine, readings: list[TransformedReading]) -> float:
    start = time.perf_counter()
    with engine.begin() as conn:
        load_batch_naive(conn, readings)
    return time.perf_counter() - start


def run_optimized(engine, readings: list[TransformedReading], batch_size: int) -> float:
    start = time.perf_counter()
    with engine.begin() as conn:
        for i in range(0, len(readings), batch_size):
            load_batch_optimized(conn, readings[i : i + batch_size])
    return time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark naive vs optimized SCADA load path")
    parser.add_argument("--rows", type=int, default=200_000)
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--skip-naive", action="store_true", help="skip the slow naive path")
    args = parser.parse_args()

    engine = get_engine()
    ensure_schema(engine)

    # Guards against a previous run having crashed mid-benchmark and left
    # synthetic rows behind - start from a known-clean state regardless.
    cleanup_benchmark_rows(engine)

    try:
        print(f"Generating {args.rows:,} synthetic readings...")
        optimized_readings = make_synthetic_readings(args.rows, "OPT")

        print("\nRunning OPTIMIZED path (COPY + staged UPSERT)...")
        optimized_time = run_optimized(engine, optimized_readings, args.batch_size)
        optimized_rate = args.rows / optimized_time
        print(f"  {args.rows:,} rows in {optimized_time:.2f}s  ({optimized_rate:,.0f} rows/sec)")

        if args.skip_naive:
            print("\n--skip-naive set: not running the naive comparison.")
            return

        naive_rows = min(args.rows, 50_000)  # naive path is too slow to run at full scale
        naive_readings = make_synthetic_readings(naive_rows, "NAIVE")
        print(
            f"\nRunning NAIVE path (row-by-row INSERT) on {naive_rows:,} rows "
            f"(capped — full-scale naive run would take too long)..."
        )
        naive_time = run_naive(engine, naive_readings)
        naive_rate = naive_rows / naive_time
        print(f"  {naive_rows:,} rows in {naive_time:.2f}s  ({naive_rate:,.0f} rows/sec)")

        naive_ms_per_row = naive_time / naive_rows * 1000
        optimized_ms_per_row = optimized_time / args.rows * 1000
        improvement = (1 - optimized_ms_per_row / naive_ms_per_row) * 100
        speedup_factor = naive_ms_per_row / optimized_ms_per_row

        print("\n" + "=" * 60)
        print(f"Naive:     {naive_ms_per_row:.3f} ms/row  ({naive_rate:,.0f} rows/sec)")
        print(f"Optimized: {optimized_ms_per_row:.3f} ms/row  ({optimized_rate:,.0f} rows/sec)")
        print(
            f"Improvement: {improvement:.1f}% lower latency per row "
            f"({speedup_factor:.1f}x throughput)"
        )
        print("=" * 60)
    finally:
        # Runs even on Ctrl-C or a mid-benchmark crash - this table is also
        # the pipeline's real curated table, so synthetic rows must never
        # be left behind for something else (e.g. the dashboard) to count.
        print("\nCleaning up synthetic OPT-/NAIVE- rows...")
        cleanup_benchmark_rows(engine)


if __name__ == "__main__":
    main()
