# SCADA Time-Series ETL Pipeline

A production-shaped ETL system for ingesting, validating, transforming, and
loading wind-turbine SCADA (Supervisory Control and Data Acquisition)
time-series data — orchestrated with **Apache Airflow**, backed by
**PostgreSQL**, modeled with **dbt**, visualized with a **FastAPI + vanilla
JS dashboard**, and containerized end-to-end with **Docker Compose**.

Three sources feed the warehouse: a physically-realistic turbine SCADA
simulator, plus two **genuinely real, live, free** external sources with no
API key required — the **Open-Meteo HTTP API** (ambient weather) and a
**NOAA NDBC ocean buoy** (real IoT hardware). See [§2](#2-data-sources).

This project reproduces, end-to-end, the kind of pipeline described by:

> "Designed and optimized ETL pipelines handling large-scale data ingestion and
> transformation for SCADA and time-series data, improving pipeline efficiency by 40%."

It includes a **benchmark suite** (`scripts/benchmark.py`) that measures a naive
row-by-row ingestion path against the optimized batch path in this repo, so the
"40% faster" claim is backed by a reproducible number rather than an assertion.

A full HTML reference doc (self-contained, opens in any browser, no server
needed) also lives at [`docs/documentation.html`](docs/documentation.html) —
this README is the text-first equivalent.

---

## Contents

0. [Overview](#0-overview)
1. [Architecture](#1-architecture)
2. [Data sources](#2-data-sources)
3. [Schema reference](#3-schema-reference)
4. [Pipeline internals](#4-pipeline-internals)
5. [Data quality framework](#5-data-quality-framework)
6. [Orchestration](#6-orchestration-airflow)
7. [Real-data wind anchoring](#7-real-data-wind-anchoring)
8. [Analytics layer (dbt)](#8-analytics-layer-dbt)
9. [Dashboard](#9-dashboard)
10. [Deployment](#10-deployment)
11. [Testing & benchmark](#11-testing--benchmark)
12. [CI/CD (GitHub Actions)](#12-cicd-github-actions)
13. [Configuration reference](#13-configuration-reference)
14. [Repository layout](#14-repository-layout)
15. [Design tradeoffs](#15-design-tradeoffs-things-id-say-in-an-interview)
16. [Roadmap](#16-roadmap--extending-this)

---

## 0. Overview

The system ingests wind-turbine SCADA readings on a 5-minute cadence,
validates them against physical and statistical rules **before** they reach
the curated table, and loads them idempotently at batch throughput. A second,
independent DAG pulls in real ambient weather and real ocean-buoy telemetry
every 15 minutes — purely to give the pipeline something external and true to
check itself against. dbt turns the curated tables into tested analytics
marts; a small dashboard makes the whole system's health and output visible
without a SQL client.

| Source | Kind | Real or simulated? |
|---|---|---|
| `src/extract/scada_simulator.py` | Simulated turbine SCADA | Simulated — real per-turbine telemetry (rotor RPM, pitch angle, nacelle temp) is proprietary to wind-farm operators and isn't published anywhere openly |
| [Open-Meteo](https://open-meteo.com) | HTTP API | **Real, live** — free, no API key |
| [NOAA NDBC](https://www.ndbc.noaa.gov) buoy 46050 | IoT (real ocean buoy, satellite telemetry) | **Real, live** — free, no API key |

Example output from a running instance (yours will differ — these are
illustrative, not persisted facts):

```text
scada_readings:  1,573 rows   (20 turbines)
rejects:             7 rows
weather_api_readings: 19 rows
iot_buoy_readings:    17 rows
pytest:              42 / 42 passing
```

---

## 1. Architecture

```
                         ┌─────────────────────────────┐
                         │        Apache Airflow        │
                         │   (scheduling, retries,      │
                         │    SLAs, alerting, backfill) │
                         └───────┬───────────────┬───────┘
                                 │               │
                     every 5 min │               │ every 15 min
                                 ▼               ▼
              ┌──────────────────────┐  ┌──────────────────────────┐
              │  scada_etl_pipeline   │  │   external_data_sources   │
              │  ─────────────────    │  │   ─────────────────────   │
              │  extract_transform_   │  │   extract_load_weather    │
              │  validate → load →    │  │   extract_load_buoy       │
              │  update_watermarks_   │  │   (independent tasks)     │
              │  and_audit            │  │                            │
              └──────────┬───────────┘  └──────────┬─────────────────┘
                         │                          │
                  reads latest                      │
                  reference wind ◄───────────────────┘  (§7 anchoring)
                         │                          │
                         ▼                          ▼
              ┌─────────────────────────────────────────────────┐
              │            PostgreSQL — public schema             │
              │  scada_readings · scada_readings_rejects ·        │
              │  extraction_watermark · pipeline_run_audit ·      │
              │  weather_api_readings · iot_buoy_readings ·       │
              │  external_data_run_audit                          │
              └───────────────┬─────────────────┬─────────────────┘
                              │                 │
                              ▼                 ▼
              ┌──────────────────────┐  ┌──────────────────────┐
              │  dbt (staging/marts)  │  │  FastAPI dashboard     │
              │  own Postgres schemas │  │  reads public schema   │
              │  staging/, marts/     │  │  directly, :3000       │
              └──────────────────────┘  └──────────────────────┘
```

**Design principles applied:**

| Principle | How it's implemented |
|---|---|
| Separation of concerns | `extract/`, `transform/`, `validation/`, `load/` are independent, unit-testable modules with no cross-imports of internals |
| Idempotency | Every load path is `INSERT ... ON CONFLICT ... DO UPDATE` keyed on the natural grain, so replaying a DAG run never duplicates rows |
| Incremental extraction | The SCADA extractor tracks a per-turbine high-water mark (`extraction_watermark`); each run only pulls new data |
| Data quality as a first-class step | Six dimensions checked before load — see [§5](#5-data-quality-framework). Failures go to a rejects table with a reason, never a silent drop |
| Decoupled failure domains | The external-source DAG is separate from the SCADA DAG specifically so a NOAA/Open-Meteo outage can't retry-storm the turbine pipeline |
| Idempotent + atomic loads | Batch `COPY` into a staging table, then a single `INSERT ... SELECT ... ON CONFLICT` inside one transaction |
| Observability | Structured JSON logging, two audit tables (`pipeline_run_audit`, `external_data_run_audit`) with real elapsed duration, Airflow SLAs + exponential-backoff retries |
| Config as code | All connection strings/thresholds via environment variables (`src/config.py`, pydantic-settings), never hardcoded |
| Schema migrations | Alembic manages schema changes (`migrations/versions/`); `sql/init.sql` mirrors it for a zero-dependency local bootstrap |
| Reproducibility | `docker compose up --build -d` brings up Postgres, both DAGs, the dashboard, and a one-shot dbt build with no manual steps |
| Testability | 42 pytest cases across extract/transform/validation, all pure-function — no live DB required |

---

## 2. Data sources

### SCADA simulator — simulated

`src/extract/scada_simulator.py` is the only module that knows "how data
enters the system" — nothing downstream generates or invents data, which is
what makes it swappable for a real OPC-UA/MQTT client without touching
anything else.

- **Power curve**: cubic ramp between cut-in (3 m/s) and rated speed
  (12 m/s), flat at rated power (3,300 kW) up to cut-out (25 m/s), zero
  above it.
- **Wind drift**: Ornstein–Uhlenbeck-style noise per turbine per tick
  (±0.4 m/s step, clamped to `[0, 28]`).
- **Injected faults (~0.5% of ticks)**: a "stuck sensor" repeating the last
  value for 2–5 ticks (comms glitch), and an out-of-range power spike
  1.2–1.8× rated (icing-induced anemometer error) — deliberately what gives
  the validation layer real work to do.
- **Reference-wind anchoring**: since [§7](#7-real-data-wind-anchoring), each
  run's fleet wind speed is anchored to the latest real Open-Meteo reading
  instead of drawn uniformly from `[4, 14]`.

### Open-Meteo — real, HTTP API

`src/extract/weather_api_extractor.py`. A plain HTTP GET, no auth, split
into `fetch_current_weather_raw()` (network) and `parse_current_weather()`
(pure) so tests exercise the parser against a fixed JSON fixture and never
touch the network.

```jsonc
// GET https://api.open-meteo.com/v1/forecast — real response
{
  "latitude": 53.54, "longitude": 8.1,
  "current": {
    "time": "2026-07-31T12:15",
    "wind_speed_10m": 3.61,
    "wind_direction_10m": 326,
    "temperature_2m": 21.2,
    "surface_pressure": 1014.0
  }
}
```

Query: `latitude=53.55&longitude=8.09` (Bremerhaven, Germany — a real North
Sea wind-energy hub), `current=wind_speed_10m,wind_direction_10m,temperature_2m,surface_pressure`,
`wind_speed_unit=ms`, `timezone=UTC`.

### NOAA NDBC buoy 46050 — real, IoT

`src/extract/iot_buoy_extractor.py`. Fetches NOAA's `realtime2` text feed
and parses the newest (first) data row. `MM` marks a missing sensor reading
and parses to `None`, never zero.

```text
# GET https://www.ndbc.noaa.gov/data/realtime2/46050.txt — real feed format
#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE
#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC  nmi  hPa    ft
2026 07 31 11 40  10  4.0  4.0   1.2    MM   6.6 191 1021.2    MM  16.8    MM   MM   MM    MM
```

Columns used: `WSPD` → `wind_speed_ms`, `GST` → `wind_gust_ms`, `WVHT` →
`wave_height_m`, `PRES` → `pressure_hpa`, `ATMP` → `air_temp_c`, `WTMP` →
`water_temp_c`.

Both real extractors run in their own DAG (`external_data_sources`),
separate from `scada_etl_pipeline`, so an outage at NOAA or Open-Meteo can't
retry-storm the turbine pipeline. Each task does fetch → validate
(`src/validation/external_validators.py`) → idempotent upsert → audit row
in `external_data_run_audit`.

---

## 3. Schema reference

Nine tables in the `public` schema, managed by Alembic
(`migrations/versions/0001_initial_schema.py`,
`0002_external_data_sources.py`), mirrored in `sql/init.sql`.

### `scada_readings` — curated, one row per turbine per timestamp

| Column | Type | Notes |
|---|---|---|
| `id` | bigserial pk | |
| `turbine_id` | varchar(20) | e.g. `WT-014`, indexed |
| `ts` | timestamptz | reading timestamp, UTC, indexed |
| `wind_speed_ms` | numeric(6,2) | |
| `power_kw` | numeric(8,2) | active power output |
| `rotor_rpm` | numeric(5,2) | |
| `nacelle_temp_c` | numeric(5,2) | |
| `pitch_angle_deg` | numeric(5,2) | |
| `status_code` | varchar(20) | operational / curtailed / fault / maintenance / offline |
| `is_anomalous` | boolean | set by the transform layer's cross-field check |
| `ingested_at` | timestamptz | pipeline load time |

Unique on `(turbine_id, ts)` — this is what makes the upsert idempotent.

### `scada_readings_rejects`

Rows that failed validation, with a human-readable reason — nothing is
silently discarded. Columns: `turbine_id`, `ts`, `raw_payload` (full
`str(dict)` of the rejected reading), `reject_reason` (`"; "`-joined failure
reasons), `rejected_at`.

### `extraction_watermark`

Per-turbine high-water mark driving incremental extraction. Columns:
`turbine_id` (pk), `last_extracted_ts` (not null).

### `pipeline_run_audit`

One row per `scada_etl_pipeline` run: `dag_run_id`, `task_id`,
`rows_extracted`/`rows_loaded`/`rows_rejected`, `duration_seconds` (real
elapsed wall time), `status`, `started_at`, `finished_at`.

### `external_data_run_audit`

Mirrors `pipeline_run_audit` for the external-sources DAG: `dag_run_id`,
`source` (`open-meteo` / `noaa-ndbc`), `rows_fetched`/`rows_loaded`/`rows_rejected`
(always 0 or 1), `duration_seconds`, `status`, timestamps.

### `weather_api_readings` — real

Unique on `(latitude, longitude, ts)`. Columns: `source` (default
`open-meteo`), `latitude`/`longitude` (numeric(6,3)), `ts`, `wind_speed_ms`,
`wind_direction_deg`, `temperature_c`, `pressure_hpa`, `ingested_at`.

### `iot_buoy_readings` — real

Unique on `(station_id, ts)`. Columns: `station_id`, `ts`, `wind_speed_ms`,
`wind_gust_ms`, `wave_height_m`, `air_temp_c`/`water_temp_c` (nullable —
NDBC's `MM`), `pressure_hpa`, `ingested_at`.

---

## 4. Pipeline internals

Four independent, pure-where-possible layers. Only `extract` and `load`
touch I/O; `transform` and `validation` are plain functions over dataclasses.

```
RawScadaReading → transform_reading() → TransformedReading
                 → validate_batch() → valid[] / failed[]
                 → load_batch_optimized() → scada_readings
```

**Transform — `src/transform/transformers.py`**

- `normalize_status_code()` — lowercases, strips, replaces spaces with
  underscores; defensive against inconsistent SCADA vendor casing.
- `flag_statistical_anomaly()` — cross-field consistency check independent
  of hard bounds: power > 50 kW at near-zero RPM, or RPM > 3 with zero
  power, is physically inconsistent even though each field alone is
  in-range.
- `transform_reading()` — pure mapping from `RawScadaReading` to
  `TransformedReading`, uppercases `turbine_id`, stamps `ingested_at`.

**Load — `src/load/loaders.py`**

`load_batch_optimized()` is the throughput path [§11](#11-testing--benchmark)'s
benchmark measures:

1. `COPY` the batch into an `UNLOGGED` staging table (`scada_readings_staging`)
   — bulk, no per-row round trip.
2. A single `INSERT ... SELECT ... FROM staging ON CONFLICT (turbine_id, ts)
   DO UPDATE`, inside one transaction.
3. `TRUNCATE` staging.

`load_batch_naive()` exists only so `scripts/benchmark.py` has something to
compare against — the production DAG never calls it.

**External loaders — `src/load/external_loaders.py`**

One row per fetch, so this is a plain idempotent `INSERT ... ON CONFLICT ...
DO UPDATE` — no throughput problem to solve at this volume.

---

## 5. Data quality framework

Every dimension below is enforced in `src/validation/validators.py` (SCADA)
or `external_validators.py` (weather/buoy). Every row-level failure lands in
a reject table with a specific reason, never a silent drop.

| Dimension | How it's checked |
|---|---|
| **Validity / accuracy** | Physical bounds: wind speed, power, rotor RPM, nacelle temperature, pitch angle — each against a configurable max in `src/config.py` |
| **Consistency** | Cross-field check: power reported with near-zero rotation, or rotation with zero power, fails even though each field is individually in-range |
| **Timeliness** | A reading timestamped more than `max_future_skew_seconds` (300s default) into the future is rejected as a bad sensor clock, not accepted as normal skew |
| **Uniqueness** | `find_batch_duplicates()` catches `(turbine_id, ts)` collisions *within* a single extract batch — before the DB's unique constraint would silently UPSERT over it |
| **Completeness** | `check_batch_completeness()` computes the exact expected row count from window × turbine_count × interval, and logs a structured warning on any shortfall |
| **Schema / required fields** | Missing `turbine_id`, missing `ts`, or an unrecognized `status_code` all fail validation explicitly |

Example rejected row, pulled from a running instance:

```text
turbine_id: WT-013
ts:         2026-07-31 11:35:01+00
reason:     power_kw 5364.23 outside [0, 3500.0]
rejected:   2026-07-31 11:38:27+00
```

That's the simulator's injected out-of-range-spike fault being caught
exactly as designed.

---

## 6. Orchestration (Airflow)

Two DAGs, two cadences, two failure domains — kept separate specifically so
an outage in one upstream system can't retry-storm the other's schedule.

### `scada_etl_pipeline` — every 5 minutes

Task graph: `extract_transform_validate` → `load` → `update_watermarks_and_audit`.
Extract/transform/validate are combined into one task deliberately — they're
pure and cheap, and splitting them would only add XCom serialization
overhead for large batches. Load and the watermark/audit update are separate
because they're the parts worth retrying and observing independently.

| Task | Does | SLA |
|---|---|---|
| `extract_transform_validate` | Reads watermarks + latest reference wind speed → generates the incremental window → simulates → transforms → validates → pushes valid/failed readings via XCom | 4 min |
| `load` | Batch COPY+UPSERT of valid readings; inserts failed readings into `scada_readings_rejects` | 3 min |
| `update_watermarks_and_audit` | Advances each turbine's watermark; computes real run duration; writes the `pipeline_run_audit` row | — |

### `external_data_sources` — every 15 minutes

Two independent tasks, no ordering dependency — `extract_load_weather` and
`extract_load_buoy` each do fetch → validate → idempotent upsert → audit
row, wrapped in their own try/finally so a failure in one never blocks the
other's audit trail.

### Shared retry policy

`retries: 3` · `retry_delay: 2 min` · exponential backoff ·
`max_retry_delay: 15 min` · `max_active_runs: 1` (prevents overlapping
`scada_etl_pipeline` runs from racing on the same watermark) ·
`catchup: False`.

---

## 7. Real-data wind anchoring

The simulator doesn't just happen to be in the same range as the real
sources — each run reads the latest real wind speed back out of Postgres and
anchors the fleet to it.

```python
# airflow/dags/scada_etl_dag.py
def _fetch_reference_wind_speed(conn) -> float | None:
    row = conn.execute(text(
        "SELECT wind_speed_ms, ts FROM weather_api_readings "
        "ORDER BY ts DESC LIMIT 1"
    )).fetchone()
    if row is None or row.wind_speed_ms is None:
        return None
    staleness = now() - row.ts
    if staleness > max_staleness:  # default 180 min
        return None
    return float(row.wind_speed_ms)
```

```python
# src/extract/scada_simulator.py
def _initial_wind_speed(self, reference_wind_speed_ms: float | None) -> float:
    if reference_wind_speed_ms is None:
        return self._rng.uniform(4, 14)  # unanchored fallback
    spread = self._rng.uniform(-REFERENCE_WIND_SPREAD_MS, REFERENCE_WIND_SPREAD_MS)
    return max(0.0, min(reference_wind_speed_ms + spread, 28.0))
```

If `weather_api_readings` is empty or stale, this returns `None` and the
simulator falls back to its original unanchored behavior — the two DAGs stay
fully decoupled; a weather-API outage degrades the simulator's realism,
never its ability to run.

**Verified effect**: triggered live while the real weather reading was
3.77 m/s, new SCADA readings landed at 1.75–6.04 m/s (mean 3.65), against
the old unanchored 4–14 m/s free range.

> **Known lag**: `marts.ambient_wind_daily_comparison` ([§8](#8-analytics-layer-dbt))
> still shows the fleet average well above the real sources on any given
> day, because it averages the *whole day's* history — including readings
> generated before anchoring went live. The daily mean converges as more
> anchored rows accumulate. See [§16](#16-roadmap--extending-this) for a fix.

---

## 8. Analytics layer (dbt)

A small dbt project sits on top of the curated tables — its own Postgres
schemas (`staging`, `marts`), kept visibly separate from `public` via a
custom `generate_schema_name` macro.

```
public.* → source() → staging.stg_* (views) → ref() → marts.* (tables)
```

**Staging models**: `stg_scada_readings`, `stg_pipeline_run_audit`,
`stg_weather_api_readings`, `stg_iot_buoy_readings` — thin pass-throughs
with light derivation (e.g. a synthetic `reading_key` for native uniqueness
tests without needing `dbt_utils`).

**Marts**:

| Mart | Grain | What it answers |
|---|---|---|
| `turbine_daily_summary` | turbine × day | Avg/max/min power, reading count, anomaly count, % operational, capacity factor (avg power ÷ rated 3,300 kW) |
| `pipeline_run_daily_summary` | day | Run count, success rate, total rows extracted/loaded/rejected, avg/max duration |
| `ambient_wind_daily_comparison` | day | **The payoff mart**: fleet avg wind speed vs. real Open-Meteo vs. real NOAA buoy, joined by day — a plausibility check against independent, externally-sourced ground truth |

```sql
-- SELECT * FROM marts.ambient_wind_daily_comparison;
 reading_date | fleet_avg_wind_speed_ms | weather_avg_wind_speed_ms | buoy_avg_wind_speed_ms
--------------+--------------------------+----------------------------+-------------------------
 2026-07-31   |                     8.58 |                       3.69 |                    3.00
```

**Tests**: 18 data tests across staging and marts — `not_null`, `unique`,
and `accepted_values` on `status_code` (matching `VALID_STATUS_CODES` in the
Python validator) and audit `status`. Full `dbt build`: **25/25 passing**
(7 models + 18 tests).

Run it: `docker compose run --rm dbt build --profiles-dir .`

---

## 9. Dashboard

`dashboard/api/main.py` (FastAPI) + `dashboard/static/` (vanilla JS +
Chart.js, no build step). Queries the same Postgres tables the pipeline
writes to, via the same `src.db.session`/`src.config` the pipeline uses —
no separate data store, no caching layer.

| Route | Returns |
|---|---|
| `GET /api/health` | Liveness check |
| `GET /api/summary` | Fleet totals, latest avg power/wind, last pipeline run |
| `GET /api/turbines/latest` | One row per turbine — its newest reading |
| `GET /api/turbines/stats` | Per-turbine aggregates: avg/max power, avg wind, anomaly count |
| `GET /api/turbines/{id}/timeseries` | Last *n* readings for one turbine (chart source) |
| `GET /api/anomalies` | Recent rows with `is_anomalous = true` |
| `GET /api/rejects` | Recent `scada_readings_rejects` rows |
| `GET /api/audit/runs` | Recent `pipeline_run_audit` rows |
| `GET /api/external` | Latest weather + buoy reading, plus recent external DAG runs |

Frontend panels: KPI row, fleet overview chart (avg power per turbine +
anomaly count), per-turbine time series (dropdown-selected), external data
sources panel (weather/buoy KPIs + recent runs), and tables for latest
readings / pipeline runs / anomalies / rejects. All panels poll every 15
seconds.

Access at **http://localhost:3000** once the stack is up.

---

## 10. Deployment

Each service that needs its own dependency set gets its own Dockerfile —
kept separate specifically to avoid three different dependency conflicts
colliding in one image.

| Service | Image | Port | Why it's separate |
|---|---|---|---|
| `postgres` | postgres:16-alpine | 5432 | — |
| `airflow-webserver` / `-scheduler` / `-init` | `Dockerfile` (apache/airflow:2.10.2) | 8081 | Base image pins SQLAlchemy 1.4.x for Airflow's own ORM |
| `dashboard` | `Dockerfile.dashboard` (python:3.11-slim) | 3000 | Free to run current SQLAlchemy 2.0 + FastAPI without fighting Airflow's pin |
| `dbt` | `Dockerfile.dbt` (python:3.11-slim) | — | Own Jinja2/click dependency graph; one-shot like `airflow-init` |

```bash
git clone <your-repo-url> scada-etl-pipeline
cd scada-etl-pipeline
cp .env.example .env

# Build and start Postgres + Airflow + dashboard + dbt
docker compose up --build -d

# Airflow UI:  http://localhost:8081  (user: admin / pass: admin)
# Dashboard:   http://localhost:3000
# Unpause the "scada_etl_pipeline" and "external_data_sources" DAGs to start scheduled runs
```

Run dbt models + tests against whatever's loaded so far (also runs once
automatically as part of `docker compose up`):

```bash
docker compose run --rm dbt build --profiles-dir .
```

---

## 11. Testing & benchmark

42 pure-function tests, zero live-DB or network dependency:

| File | Cases | Covers |
|---|---|---|
| `test_validation.py` | 13 | Bounds, timeliness, batch duplicate detection, completeness check |
| `test_extract.py` | 12 | Power curve shape, incremental window logic, wind-speed anchoring & determinism |
| `test_transform.py` | 7 | Status normalization, anomaly flagging |
| `test_iot_buoy_extractor.py` | 5 | realtime2 parsing, missing-value handling, validation |
| `test_weather_api_extractor.py` | 5 | Open-Meteo response parsing, validation |
| **Total** | **42** | |

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

**Benchmark — `scripts/benchmark.py`**: what turns "improved pipeline
efficiency by 40%" from a claim into a reproducible number. Generates
synthetic readings, times the naive row-by-row `INSERT` path against the
optimized COPY+staged-UPSERT path, prints ms/row and the throughput
multiplier. (The naive path is capped at 50,000 rows in the comparison —
run to completion at full scale, it's too slow to be worth waiting for.)

```bash
python scripts/benchmark.py --rows 500000
```

---

## 12. CI/CD (GitHub Actions)

Live at [github.com/allmamun556/pyspark-etl-toy/actions](https://github.com/allmamun556/pyspark-etl-toy/actions) —
`.github/workflows/scada-etl-pipeline-ci.yml`, runs on every push/PR that
touches this project.

> **A real gotcha worth documenting**: this project lives nested inside a
> monorepo (`pyspark-etl-toy`). GitHub Actions only discovers workflow files
> at `.github/workflows/` relative to the **true repository root** — a
> workflow file placed at
> `data_engineer_tasks/scada-etl-pipeline/.github/workflows/` (i.e. mirroring
> this project's own directory as if it were the repo root) is silently
> ignored; GitHub never registers it, so nothing ever triggers. The workflow
> file has to live at the monorepo's actual root, `paths:`-filtered so it
> only fires on changes under `data_engineer_tasks/scada-etl-pipeline/**`,
> with every step's working directory and Docker build context pointed at
> the project subfolder explicitly.

| Job | What it validates | Last run |
|---|---|---|
| `lint-and-test` | `ruff check .` + all 42 pytest cases (installs `requirements.txt` minus `apache-airflow`, since nothing under test imports it and it needs its own constraints file to install reliably) | ✅ 30s |
| `migrations-and-dbt` | Spins up a real `postgres:16-alpine` service container, runs `alembic upgrade head` against it from empty, then `dbt build` — catches schema/dbt drift that pytest structurally can't since it never touches a live DB | ✅ 56s |
| `docker-build` | Builds all three Dockerfiles (Airflow, dashboard, dbt) with GitHub Actions layer caching, to catch Dockerfile rot without running the full stack | ✅ 2m29s |

Pushing to GitHub also required granting the `gh` CLI's OAuth token the
`workflow` scope (`gh auth refresh -h github.com -s workflow`) — GitHub
requires that scope specifically to create or modify anything under
`.github/workflows/`, as a deliberate guard against an app silently
planting CI automation.

---

## 13. Configuration reference

`src/config.py` — a single `pydantic-settings` class, cached with
`@lru_cache`, reading from environment variables or a local `.env`.

| Setting | Default | Purpose |
|---|---|---|
| `postgres_host/port/db/user/password` | localhost:5432 / scada | Connection, identical shape across pipeline/dashboard/dbt |
| `turbine_count` | 20 | Fleet size the simulator generates |
| `reading_interval_seconds` | 600 | 10-min SCADA interval (typical in wind) |
| `load_batch_size` | 5000 | Rows per COPY batch |
| `max_wind_speed_ms` | 45.0 | Validation ceiling |
| `max_power_kw` | 3500.0 | Validation ceiling |
| `max_rotor_rpm` | 20.0 | Validation ceiling |
| `min_nacelle_temp_c` / `max_nacelle_temp_c` | -30 / 60 | Validation range |
| `max_future_skew_seconds` | 300 | Timeliness check tolerance |
| `weather_api_base_url` | `api.open-meteo.com/v1/forecast` | HTTP source endpoint |
| `weather_latitude` / `weather_longitude` | 53.55 / 8.09 | Bremerhaven, DE |
| `iot_buoy_base_url` | `ndbc.noaa.gov/data/realtime2` | IoT source endpoint |
| `iot_buoy_station_id` | `46050` | Stonewall Bank, OR |
| `http_request_timeout_seconds` | 10 | Both external extractors |
| `reference_wind_max_staleness_minutes` | 180 | [§7](#7-real-data-wind-anchoring) anchoring freshness cutoff |
| `log_level` | `INFO` | Structured JSON logging |

---

## 14. Repository layout

```
scada-etl-pipeline/
├── airflow/dags/
│   ├── scada_etl_dag.py              # turbine SCADA — every 5 min
│   └── external_data_dag.py          # weather + buoy — every 15 min
├── src/
│   ├── config.py                     # every setting, env-driven
│   ├── extract/
│   │   ├── scada_simulator.py        # simulated SCADA feed
│   │   ├── weather_api_extractor.py  # real HTTP API: Open-Meteo
│   │   └── iot_buoy_extractor.py     # real IoT: NOAA NDBC
│   ├── transform/transformers.py     # cleaning, derived metrics, anomaly flags
│   ├── validation/
│   │   ├── validators.py             # SCADA: 6 DQ dimensions
│   │   └── external_validators.py    # weather/buoy bounds
│   ├── load/
│   │   ├── loaders.py                # batch COPY + idempotent UPSERT
│   │   └── external_loaders.py       # single-row idempotent UPSERT
│   ├── db/{models.py, session.py}    # SQLAlchemy ORM + engine/session
│   └── utils/logging_config.py       # structured JSON logging
├── dbt/models/{staging,marts}/       # analytics models on the curated tables
├── dashboard/
│   ├── api/main.py                   # FastAPI read API
│   └── static/                       # vanilla JS + Chart.js frontend
├── docs/documentation.html           # full self-contained HTML reference doc
├── migrations/versions/              # 0001_initial_schema, 0002_external_data_sources
├── sql/init.sql                      # bootstrap DDL, mirrors Alembic
├── scripts/benchmark.py              # naive vs optimized load benchmark
├── tests/                            # 42 cases, 5 files
├── docker-compose.yml                # postgres + airflow + dashboard + dbt
├── Dockerfile                        # Airflow image
├── Dockerfile.dashboard              # Dashboard API image
├── Dockerfile.dbt                    # dbt image
├── requirements.txt / requirements-dashboard.txt / requirements-dbt.txt
└── .env.example
```

> **Not shown above**: `.github/workflows/scada-etl-pipeline-ci.yml` — it
> has to live at the *true* git repository root, one level up from this
> project (see [§12](#12-cicd-github-actions) for why), so it isn't part of
> this directory's own tree.

---

## 15. Design tradeoffs (things I'd say in an interview)

- **Airflow over cron**: retries with backoff, SLA-miss alerting, backfill
  support, and a visual DAG are worth the extra operational overhead once
  there are more than a couple of interdependent jobs.
- **Batch COPY + staging table over row-by-row INSERT**: this is the single
  biggest lever for the throughput improvement — see `scripts/benchmark.py`.
- **Reject table over dropping bad rows**: SCADA sensors fail in ways that
  look like real data (stuck values, out-of-range spikes from icing, comms
  glitches); silently dropping those rows makes downstream
  availability/power-curve analyses wrong in a way nobody notices until much
  later.
- **Watermark-based incremental extraction over full reload**: SCADA
  archives grow unbounded; re-scanning everything every run doesn't scale.
- **Two DAGs instead of one**: an outage at NOAA or Open-Meteo is a real,
  external, unpredictable failure mode. Isolating it into its own DAG means
  it can retry and eventually fail on its own schedule without ever
  touching the turbine pipeline's SLA.
- **A separate image per service instead of one shared image**: Airflow's
  base image pins SQLAlchemy 1.4.x for its own ORM; the dashboard and dbt
  both want current-generation dependencies. Three Dockerfiles avoids a
  three-way dependency resolution fight inside one image.

---

## 16. Roadmap / extending this

- Swap the simulator in `src/extract/scada_simulator.py` for a real
  OPC-UA / MQTT client or a historian export — the rest of the pipeline is
  source-agnostic by construction.
- Swap PostgreSQL for TimescaleDB by adding
  `SELECT create_hypertable('scada_readings', 'ts')` in a migration —
  schema stays identical.
- Pull additional NDBC stations (or Open-Meteo's forecast endpoint, not
  just `current`) to build a proper time series per external source instead
  of one point-in-time reading per DAG run.
- `ambient_wind_daily_comparison`'s daily average is a same-day blend of
  pre- and post-anchoring readings until older rows age out — a rolling
  window (e.g. "last 2 hours") would show the anchoring's effect
  immediately instead of waiting for it to dominate the daily mean.
- Add a dbt test (or `dbt-expectations`) asserting the fleet/weather/buoy
  wind speeds in `ambient_wind_daily_comparison` stay within a plausible
  delta of each other — turns the comparison mart from observational into
  an alertable data-quality gate.
