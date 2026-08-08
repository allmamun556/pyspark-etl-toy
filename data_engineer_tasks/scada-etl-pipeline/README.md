# SCADA Time-Series ETL Pipeline

A production-shaped ETL system for ingesting, validating, transforming, and
loading wind-turbine SCADA (Supervisory Control and Data Acquisition)
time-series data — orchestrated with **Apache Airflow**, backed by
**PostgreSQL**, modeled with **dbt**, visualized with a **FastAPI + vanilla
JS dashboard**, and containerized end-to-end with **Docker Compose**.

Four sources feed the warehouse: two physically-realistic simulated fleets
(wind turbines and solar PV plants), plus two **genuinely real, live, free**
external sources with no API key required — the **Open-Meteo HTTP API**
(ambient weather + solar irradiance) and a **NOAA NDBC ocean buoy** (real IoT
hardware). Both simulated fleets anchor themselves to the real sources
rather than drifting on pure noise. See [§2](#2-data-sources).

This project reproduces, end-to-end, the kind of pipeline described by:

> "Designed and optimized ETL pipelines handling large-scale data ingestion and
> transformation for SCADA and time-series data, improving pipeline efficiency by 40%."

It includes a **benchmark suite** (`scripts/benchmark.py`) that measures a naive
row-by-row ingestion path against the optimized batch path in this repo, so the
"40% faster" claim is backed by a reproducible number rather than an assertion.

A full HTML reference doc (self-contained, opens in any browser, no server
needed) also lives at [`docs/documentation.html`](docs/documentation.html) —
this README is the text-first equivalent. Published live at
**https://allmamun556.github.io/pyspark-etl-toy/**, alongside the dbt docs
lineage/schema browser at **/dbt-docs/** ([§8](#8-analytics-layer-dbt), [§12](#12-cicd-github-actions)).

---

## Contents

0. [Overview](#0-overview)
1. [Architecture](#1-architecture)
2. [Data sources](#2-data-sources)
3. [Schema reference](#3-schema-reference)
4. [Pipeline internals](#4-pipeline-internals)
5. [Data quality framework](#5-data-quality-framework)
6. [Orchestration](#6-orchestration-airflow)
7. [Real-data anchoring (wind + solar)](#7-real-data-anchoring-wind--solar)
8. [Analytics layer (dbt)](#8-analytics-layer-dbt)
9. [Dashboard](#9-dashboard)
10. [Deployment](#10-deployment)
11. [Testing & benchmark](#11-testing--benchmark)
12. [CI/CD (GitHub Actions)](#12-cicd-github-actions)
13. [Configuration reference](#13-configuration-reference)
14. [Repository layout](#14-repository-layout)
15. [Design tradeoffs](#15-design-tradeoffs-things-id-say-in-an-interview)
16. [Roadmap](#16-roadmap--extending-this)

**Looking for a specific topic?**

| Topic | Where |
|---|---|
| Problem statement, goals, methodology, results | [§0](#0-overview), below |
| System / backend architecture | [§1](#1-architecture), [§4](#4-pipeline-internals), [§6](#6-orchestration-airflow) |
| Database design (schema, keys, hypertables, migrations) | [§3](#3-schema-reference) |
| Frontend / dashboard services | [§9](#9-dashboard) |
| Data quality & validation | [§5](#5-data-quality-framework) |
| Analytics / data modeling | [§8](#8-analytics-layer-dbt) |
| Testing, benchmark, and results | [§11](#11-testing--benchmark) |
| Deployment & CI/CD | [§10](#10-deployment), [§12](#12-cicd-github-actions) |
| Every config value | [§13](#13-configuration-reference) |

---

## 0. Overview

### Problem statement

Data-engineer job postings and resumes routinely claim things like
*"designed and optimized ETL pipelines handling large-scale data ingestion
and transformation for SCADA and time-series data, improving pipeline
efficiency by 40%."* That sentence is unverifiable as written — there's no
code to read, no number to reproduce, and no way to tell whether "40%"
came from a real measurement or was picked because it sounds credible. Real
per-turbine SCADA telemetry is also proprietary to wind-farm operators and
isn't published anywhere openly, so a portfolio project in this domain
can't just download a public dataset the way it could for, say, retail
sales data — the data itself has to be built, not just processed.

The problem this project sets out to solve: **build a production-shaped
SCADA/time-series ETL system, end to end, where every claim a resume line
like that one would make is backed by code that runs and a number that
reproduces** — not an assertion, a screenshot, or a toy script that only
handles the happy path.

### Goals

1. **Reproduce a realistic ingestion domain** without access to real
   hardware — a physically modeled wind-turbine SCADA simulator and a
   second, independent solar-PV-plant simulator, each with genuine sensor
   fault injection (stuck values, out-of-range spikes) so the data quality
   layer has real work to do, not clean data with nothing to catch.
2. **Ground the simulation in reality** rather than let it drift on pure
   noise — anchor both simulated fleets to genuinely real, live, free
   external data (Open-Meteo weather API, a NOAA NDBC ocean buoy) ([§7](#7-real-data-anchoring-wind--solar)).
3. **Prove the throughput claim**, not assert it — a reproducible benchmark
   comparing a naive row-by-row load path against an optimized batch path,
   with a real number either backing or contradicting "40% faster" ([§11](#11-testing--benchmark)).
4. **Build in the concerns a production pipeline actually has** and a toy
   script doesn't: idempotent recovery from retries and overlapping windows,
   data-quality gates before data reaches curated tables, observability
   (structured logs, audit tables, Slack alerting), bounded storage growth
   (retention policies), and CI that actually executes the pipeline rather
   than just linting it.
5. **Make it fully inspectable and runnable by anyone** — `docker compose up
   --build -d` and the whole stack (database, orchestrator, transform
   layer, analytics layer, dashboard) comes up with no manual setup, and
   every design decision is documented with the reasoning behind it, not
   just the what.

### Methodology

- **Layered architecture, not a monolith**: `extract/` → `transform/` →
  `validation/` → `load/` are independent, unit-testable modules with no
  cross-imports of internals ([§1](#1-architecture), [§4](#4-pipeline-internals)).
- **Simulate, but simulate honestly**: every simulated value is generated
  by an explicit physical model (a cubic wind power curve, a clear-sky
  solar irradiance curve, NOCT panel heating) with its assumptions and
  simplifications documented, not a black box or a hardcoded fixture
  ([§2](#2-data-sources)).
- **Orchestrate with Airflow, not cron**: three DAGs, retries with
  exponential backoff, SLA tracking, and failure alerting — because a
  scheduled shell script doesn't give you any of that for free ([§6](#6-orchestration-airflow)).
- **Verify live, at every step, not just at the end**: throughout this
  project's development, every change was checked against a real running
  system (a live Postgres, a live Airflow scheduler, a live CI run) before
  being called done — this surfaced and fixed real bugs a purely local, no
  verification workflow would have shipped silently (documented as they
  happened in [§12](#12-cicd-github-actions)'s CI gotchas).
- **Test what pytest can reach with pytest; test what needs a live database
  against a live database**: 73 pure-function unit tests for
  extract/transform/validation logic, plus separate live-database checks
  (`airflow dags test`, `scripts/verify_idempotency.py`, `dbt build`) for
  everything that genuinely needs one — rather than mocking a database to
  inflate a coverage number ([§11](#11-testing--benchmark)).
- **Document the why, not just the what**: every non-obvious decision in
  this README states the tradeoff it was weighed against ([§15](#15-design-tradeoffs-things-id-say-in-an-interview)),
  and real incidents hit during development are documented rather than
  smoothed over, because the reasoning is more useful to a reader than a
  claim that nothing ever went wrong.

### Results

| Metric | Result |
|---|---|
| Unit tests | 73/73 passing, 89% coverage on the modules they cover (85% CI gate) |
| dbt tests | 37/37 passing (10 models + 27 data tests) |
| Live DAG execution in CI | `scada_etl_pipeline` and `solar_etl_pipeline` run end-to-end against a real database on every push |
| Idempotency | Verified against a real database, not just asserted — replay and overlapping-window scenarios both hold ([§11](#11-testing--benchmark)) |
| Benchmark | Naive row-by-row `INSERT` vs. optimized COPY+staged-UPSERT, run yourself with `python scripts/benchmark.py` ([§11](#11-testing--benchmark)) |
| Data sources | 2 genuinely real, live, free external sources; 2 simulated fleets anchored to them, not drifting on noise |
| CI/CD | 4 jobs (lint+coverage, migrations+dbt+DAG execution, Docker build+GHCR push, Pages deploy), all green on every push |
| Live artifacts | Dashboard (2 pages, 4 charts + 2 tables each), dbt docs site published to GitHub Pages, Docker images published to GHCR |
| Real incidents caught and fixed during development | A CI dependency conflict (`typing_extensions`/`sqlalchemy` vs. Airflow), a stale-XCom false alarm ruled out via isolated re-testing, and a monorepo-wide accidental reformat caught and reverted before it was ever committed — all documented in place rather than hidden ([§12](#12-cicd-github-actions)) |

The system ingests wind-turbine SCADA and solar PV plant readings on a
5-minute cadence each, validates them against physical and statistical
rules **before** they reach the curated tables, and loads them idempotently
at batch throughput. A third, independent DAG pulls in real ambient weather
and real ocean-buoy telemetry every 15 minutes — purely to give both
simulated pipelines something external and true to check themselves
against (and, since [§7](#7-real-data-anchoring-wind--solar), to anchor
their output to). dbt turns the curated tables into tested analytics
marts; a small dashboard makes the whole system's health and output visible
without a SQL client.

| Source | Kind | Real or simulated? |
|---|---|---|
| `src/extract/scada_simulator.py` | Simulated turbine SCADA | Simulated — real per-turbine telemetry (rotor RPM, pitch angle, nacelle temp) is proprietary to wind-farm operators and isn't published anywhere openly |
| `src/extract/solar_simulator.py` | Simulated PV plant fleet | Simulated — same reasoning as wind; anchored to real irradiance ([§7](#7-real-data-anchoring-wind--solar)) |
| [Open-Meteo](https://open-meteo.com) | HTTP API | **Real, live** — free, no API key |
| [NOAA NDBC](https://www.ndbc.noaa.gov) buoy 46050 | IoT (real ocean buoy, satellite telemetry) | **Real, live** — free, no API key |

Example output from a running instance (yours will differ — these are
illustrative, not persisted facts):

```text
scada_readings:  22,306 rows   (20 turbines)
solar_readings:      72 rows   (8 plants)
rejects (wind):      54 rows
weather_api_readings: 20 rows  (incl. real shortwave_radiation_w_m2)
iot_buoy_readings:    19 rows
pytest:              73 / 73 passing
```

---

## 1. Architecture

```
                                  ┌─────────────────────────────┐
                                  │        Apache Airflow        │
                                  │   (scheduling, retries,      │
                                  │    SLAs, alerting, backfill) │
                                  └───────┬───────────┬───────┬───┘
                                          │           │       │
                             every 5 min  │           │       │ every 15 min
                                          ▼           ▼       ▼
                 ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐
                 │ scada_etl_pipeline│ │ solar_etl_pipeline│ │  external_data_sources    │
                 │ ───────────────── │ │ ───────────────── │ │  ─────────────────────    │
                 │ extract_transform_│ │ extract_transform_│ │  extract_load_weather     │
                 │ validate → load → │ │ validate → load → │ │  extract_load_buoy        │
                 │ update_watermarks_│ │ update_watermarks_│ │  (independent tasks)      │
                 │ and_audit         │ │ and_audit         │ │                           │
                 └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────────────┘
                           │        reads latest  │                    │
                           │◄──── reference wind ──┼──── reference ─────┤
                           │        + irradiance   │     irradiance     │  (§7 anchoring)
                           ▼                       ▼                    ▼
              ┌───────────────────────────────────────────────────────────────────┐
              │              TimescaleDB (PostgreSQL) — public schema               │
              │  scada_readings · scada_readings_rejects · extraction_watermark ·  │
              │  solar_readings · solar_readings_rejects ·                        │
              │  solar_extraction_watermark · pipeline_run_audit (shared) ·        │
              │  weather_api_readings · iot_buoy_readings · external_data_run_audit│
              │  scada_readings / solar_readings are hypertables, 90-day retention │
              └──────────────────────┬────────────────────────┬────────────────────┘
                                     │                        │
                                     ▼                        │
                        ┌──────────────────────┐              │
                        │  dbt (staging/marts)  │              │
                        │  own Postgres schemas │              │
                        │  staging/, marts/     │              │
                        └───────────┬──────────┘              │
                                    │ reads marts for          │
                                    │ per-asset stats          │
                                    ▼                          ▼
                        ┌────────────────────────────────────────┐
                        │           FastAPI dashboard              │
                        │  stats endpoints → marts.*; everything   │
                        │  else → public schema directly, :3000    │
                        └────────────────────────────────────────┘

DAG task failures also fire a Slack webhook (on_failure_callback,
safe no-op when SLACK_WEBHOOK_URL is unset) — not shown above to keep
the data-flow diagram readable; see §6.
```

**Design principles applied:**

| Principle | How it's implemented |
|---|---|
| Separation of concerns | `extract/`, `transform/`, `validation/`, `load/` are independent, unit-testable modules with no cross-imports of internals |
| Idempotency | Every load path is `INSERT ... ON CONFLICT ... DO UPDATE` keyed on the natural grain, so replaying a DAG run never duplicates rows |
| Incremental extraction | Both simulated fleets track a high-water mark per asset (`extraction_watermark` / `solar_extraction_watermark`); each run only pulls new data |
| Reuse where it genuinely fits | `scada_etl_pipeline` and `solar_etl_pipeline` share `pipeline_run_audit` (same shape, distinguished by `task_id`) rather than duplicating an audit table per fleet — but each gets its own readings/rejects/watermark tables, since those genuinely differ |
| Data quality as a first-class step | Six dimensions checked before load — see [§5](#5-data-quality-framework). Failures go to a rejects table with a reason, never a silent drop |
| Decoupled failure domains | The external-source DAG is separate from the SCADA DAG specifically so a NOAA/Open-Meteo outage can't retry-storm the turbine pipeline |
| Idempotent + atomic loads | Batch `COPY` into a staging table, then a single `INSERT ... SELECT ... ON CONFLICT` inside one transaction |
| Observability | Structured JSON logging, two audit tables (`pipeline_run_audit`, `external_data_run_audit`) with real elapsed duration, Airflow SLAs + exponential-backoff retries, Slack failure alerts (`on_failure_callback`, safe no-op when unconfigured — [§6](#6-orchestration-airflow)) |
| Config as code | All connection strings/thresholds via environment variables (`src/config.py`, pydantic-settings), never hardcoded |
| Schema migrations | Alembic manages schema changes (`migrations/versions/`); `sql/init.sql` mirrors it for a zero-dependency local bootstrap |
| Bounded storage growth | `scada_readings`/`solar_readings` are TimescaleDB hypertables with a 90-day retention policy — old chunks drop themselves on TimescaleDB's own schedule instead of the tables growing forever ([§3](#3-schema-reference)) |
| Single source of truth for aggregates | The dashboard's per-turbine/per-plant stats endpoints read dbt's `marts.*` tables instead of re-deriving the same aggregation SQL a second time ([§9](#9-dashboard)) |
| Reproducibility | `docker compose up --build -d` brings up Postgres, all three DAGs, the dashboard, and a one-shot dbt build with no manual steps; every dependency set is pinned via a `pip-compile`-generated lockfile; CI publishes built images to GHCR on every `master` push ([§10](#10-deployment)) |
| Testability | 73 pytest cases across extract/transform/validation/alerting (89% coverage, gated at 85% — [§11](#11-testing--benchmark)), all pure-function — no live DB required; `airflow dags test` runs the real DAGs end-to-end in CI, and `scripts/verify_idempotency.py` proves the upsert claim against a real database rather than leaving it as a design assertion ([§12](#12-cicd-github-actions)) |
| Silent-failure detection | dbt source freshness on `scada_readings`/`solar_readings` catches "the DAG stopped running" - a failure mode with zero bad rows, just zero rows, that row-level validation structurally can't see ([§8](#8-analytics-layer-dbt)) |
| Fast local feedback | Pre-commit hooks run the same `ruff check`/`ruff format` CI runs, before a push instead of after - scoped to this directory, since the repo is a monorepo ([§10](#10-deployment)) |

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
- **Reference-wind anchoring**: since [§7](#7-real-data-anchoring-wind--solar), each
  run's fleet wind speed is anchored to the latest real Open-Meteo reading
  instead of drawn uniformly from `[4, 14]`.

### Solar plant simulator — simulated

`src/extract/solar_simulator.py`. Same reasoning and same shape as the wind
simulator - real per-plant inverter telemetry is proprietary, so this
simulates a fleet of 8 PV plants (5 MWp DC / 4.5 MW AC each by default).

- **Clear-sky irradiance model**: sinusoidal curve between fixed sunrise
  (06:00 UTC) and sunset (18:00 UTC), peaking at 950 W/m² - a deliberate
  simplification (no solar-position math for the plant's actual
  latitude/date), noted rather than left silently wrong.
- **Panel heating**: NOCT model (45°C at 800 W/m², 20°C ambient, 1 m/s
  wind - a standard PV datasheet spec), then a crystalline-silicon
  temperature derate of 0.4%/°C above the 25°C STC baseline.
- **Cloud cover**: an Ornstein-Uhlenbeck-style `cloud_factor` per plant
  (same drift pattern as wind's `base_wind_ms`), so output wanders
  realistically instead of following the clear-sky curve exactly.
- **True night is exactly zero** - irradiance, DC power, and AC power all
  read `0.0` outside daylight hours, not a noise-driven near-zero value.
  (An earlier version added sensor noise unconditionally and occasionally
  produced ~75 kW of "output" at 2 AM; fixed by gating noise on `clear_sky > 0`.)
- **Injected faults (~0.5% of ticks)**: a stuck irradiance sensor (comms
  glitch, 2-5 ticks), and an inverter trip - full sun available but AC
  output drops to zero from a simulated grid fault.
- **Reference-irradiance anchoring**: mirrors the wind simulator exactly
  (see [§7](#7-real-data-anchoring-wind--solar)), anchored to Open-Meteo's real
  `shortwave_radiation` field instead of Open-Meteo's wind speed.

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
    "time": "2026-08-07T13:30",
    "wind_speed_10m": 3.72,
    "wind_direction_10m": 310,
    "temperature_2m": 19.8,
    "surface_pressure": 1016.0,
    "shortwave_radiation": 605.0
  }
}
```

Query: `latitude=53.55&longitude=8.09` (Bremerhaven, Germany — a real North
Sea wind-energy hub), `current=wind_speed_10m,wind_direction_10m,temperature_2m,surface_pressure,shortwave_radiation`,
`wind_speed_unit=ms`, `timezone=UTC`. `shortwave_radiation` is the field
that anchors the solar simulator — one HTTP fetch feeds both the wind and
solar pipelines' reference values.

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
separate from `scada_etl_pipeline` and `solar_etl_pipeline`, so an outage at
NOAA or Open-Meteo can't retry-storm either simulated pipeline. Each task
does fetch → validate (`src/validation/external_validators.py`) →
idempotent upsert → audit row in `external_data_run_audit`. This isn't
theoretical: while building this, Open-Meteo returned a genuine `503
Service Unavailable` mid-session — the DAG recorded `status="failed"`
accurately (0 rows loaded, not a false success) and Airflow's own retry
picked it up automatically.

---

## 3. Schema reference

Thirteen tables in the `public` schema, managed by Alembic
(`migrations/versions/0001_initial_schema.py`,
`0002_external_data_sources.py`, `0003_solar_energy_source.py`,
`0004_timescaledb_hypertables.py`), mirrored in `sql/init.sql`.

### `scada_readings` — curated, one row per turbine per timestamp

**TimescaleDB hypertable**, chunked automatically on `ts`, with a 90-day
retention policy (`add_retention_policy`) — old chunks are dropped entirely
on TimescaleDB's own background schedule rather than the table growing
without bound. This is the reason the primary key is composite: TimescaleDB
requires every unique index/primary key on a hypertable to include the
partitioning column, so `id` alone can't be the key once it's a hypertable.

| Column | Type | Notes |
|---|---|---|
| `id` | bigserial | part of the composite primary key below |
| `turbine_id` | varchar(20) | e.g. `WT-014`, indexed |
| `ts` | timestamptz | reading timestamp, UTC, indexed; hypertable partitioning column |
| `wind_speed_ms` | numeric(6,2) | |
| `power_kw` | numeric(8,2) | active power output |
| `rotor_rpm` | numeric(5,2) | |
| `nacelle_temp_c` | numeric(5,2) | |
| `pitch_angle_deg` | numeric(5,2) | |
| `status_code` | varchar(20) | operational / curtailed / fault / maintenance / offline |
| `is_anomalous` | boolean | set by the transform layer's cross-field check |
| `ingested_at` | timestamptz | pipeline load time |

Primary key `(id, ts)`; unique on `(turbine_id, ts)` — the latter is what
makes the upsert idempotent.

### `scada_readings_rejects`

Rows that failed validation, with a human-readable reason — nothing is
silently discarded. Columns: `turbine_id`, `ts`, `raw_payload` (full
`str(dict)` of the rejected reading), `reject_reason` (`"; "`-joined failure
reasons), `rejected_at`.

### `extraction_watermark`

Per-turbine high-water mark driving incremental extraction. Columns:
`turbine_id` (pk), `last_extracted_ts` (not null).

### `solar_readings` — curated, one row per plant per timestamp

Also a **TimescaleDB hypertable** with the same 90-day retention policy and
composite `(id, ts)` primary key as `scada_readings` above, for the same
reason — it's the fleet's other high-volume, ever-growing time-series table.

| Column | Type | Notes |
|---|---|---|
| `plant_id` | varchar(20) | e.g. `SP-004`, indexed |
| `ts` | timestamptz | reading timestamp, UTC, indexed; hypertable partitioning column |
| `irradiance_w_m2` | numeric(6,2) | |
| `panel_temp_c` | numeric(5,2) | NOCT-modeled |
| `dc_power_kw` | numeric(8,2) | before inverter conversion |
| `ac_power_kw` | numeric(8,2) | after inverter conversion + clipping |
| `inverter_efficiency_pct` | numeric(5,2) | |
| `status_code` | varchar(20) | operational / night / curtailed / fault / maintenance / offline |
| `is_anomalous` | boolean | set by the transform layer's cross-field check |
| `ingested_at` | timestamptz | pipeline load time |

Primary key `(id, ts)`; unique on `(plant_id, ts)`. `solar_readings_rejects`
and `solar_extraction_watermark` mirror `scada_readings_rejects` and
`extraction_watermark` exactly, keyed on `plant_id` instead of `turbine_id`
(and are plain tables, not hypertables — one row per reject/watermark
update, not a genuine time series).

### `pipeline_run_audit` — shared between both simulated fleets

One row per `scada_etl_pipeline` **or** `solar_etl_pipeline` run: `dag_run_id`,
`task_id` (doubles as the pipeline name - this is how a row is attributed to
one fleet or the other), `rows_extracted`/`rows_loaded`/`rows_rejected`,
`duration_seconds` (real elapsed wall time), `status`, `started_at`,
`finished_at`. Reused rather than duplicated per fleet since the shape is
identical either way.

### `external_data_run_audit`

Mirrors `pipeline_run_audit` for the external-sources DAG: `dag_run_id`,
`source` (`open-meteo` / `noaa-ndbc`), `rows_fetched`/`rows_loaded`/`rows_rejected`
(always 0 or 1), `duration_seconds`, `status`, timestamps.

### `weather_api_readings` — real

Unique on `(latitude, longitude, ts)`. Columns: `source` (default
`open-meteo`), `latitude`/`longitude` (numeric(6,3)), `ts`, `wind_speed_ms`,
`wind_direction_deg`, `temperature_c`, `pressure_hpa`,
`shortwave_radiation_w_m2` (added in `0003_solar_energy_source.py` — the
solar simulator's anchor field), `ingested_at`.

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

**Solar plant fleet — `solar_transformers.py` / `solar_validators.py` / `solar_loaders.py`**

Structurally identical to the wind path above (`RawSolarReading →
TransformedSolarReading → validate_solar_batch() →
load_solar_batch_optimized() → solar_readings`), reusing
`normalize_status_code()` from `transformers.py` since status-code cleanup
isn't source-specific. `flag_solar_anomaly()` is the solar equivalent of
`flag_statistical_anomaly()`: meaningful irradiance with no output, or
output with no irradiance, is physically inconsistent.

---

## 5. Data quality framework

Every dimension below is enforced in `src/validation/validators.py` (SCADA),
`solar_validators.py` (solar - same six dimensions, `plant_id` instead of
`turbine_id`), or `external_validators.py` (weather/buoy). Every row-level
failure lands in a reject table with a specific reason, never a silent drop.

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

Three DAGs, two distinct cadences, three failure domains — kept separate
specifically so an outage in one upstream system can't retry-storm another
DAG's schedule.

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

### `solar_etl_pipeline` — every 5 minutes

Structurally identical task graph and SLAs to `scada_etl_pipeline` above -
same three tasks, same reasoning for why they're split the way they are.
The only real differences: it reads/writes `solar_extraction_watermark`
instead of `extraction_watermark`, and its `update_watermarks_and_audit`
task calls the *same* `record_run_audit()` function as the wind DAG
(imported from `src.load.loaders`) rather than a duplicated one, writing to
the shared `pipeline_run_audit` table with `task_id="solar_etl_pipeline"`.

### `external_data_sources` — every 15 minutes

Two independent tasks, no ordering dependency — `extract_load_weather` and
`extract_load_buoy` each do fetch → validate → idempotent upsert → audit
row, wrapped in their own try/finally so a failure in one never blocks the
other's audit trail.

### Shared retry policy

`retries: 3` · `retry_delay: 2 min` · exponential backoff ·
`max_retry_delay: 15 min` · `max_active_runs: 1` per DAG (prevents
overlapping runs of the same DAG from racing on the same watermark) ·
`catchup: False`.

### Failure alerting

All three DAGs set `on_failure_callback: notify_dag_failure`
(`src/utils/alerting.py`) in their shared `DEFAULT_ARGS`. When a task
exhausts its retries, it posts the DAG id, task id, run id, and Airflow log
URL to a Slack incoming webhook.

```python
# src/utils/alerting.py
def notify_dag_failure(context: dict) -> None:
    settings = get_settings()
    if not settings.slack_webhook_url:
        logger.info("slack_webhook_url not configured - skipping failure notification")
        return
    ...
    requests.post(settings.slack_webhook_url, json={"text": text}, timeout=...)
```

Safe-by-default: with `SLACK_WEBHOOK_URL` unset (the default — see
[§13](#13-configuration-reference)), this is a no-op logged at `INFO`, not a
crash or a silently-swallowed exception. Any error posting to Slack itself
(webhook down, network blip) is caught and logged, never re-raised — a
notification failure must never fail the task that triggered it. Covered by
`tests/test_alerting.py` (3 cases: no-op when unconfigured, correct payload
when configured, exceptions swallowed).

---

## 7. Real-data anchoring (wind + solar)

Neither simulator just happens to be in the same range as the real sources
— each run reads the latest matching real value back out of Postgres and
anchors its fleet to it. Both fleets follow the identical pattern; wind is
shown first, solar right after.

### Wind

```python
# airflow/dags/scada_etl_dag.py
def _fetch_reference_wind_speed(conn) -> float | None:
    row = conn.execute(
        text("SELECT wind_speed_ms, ts FROM weather_api_readings ORDER BY ts DESC LIMIT 1")
    ).fetchone()
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

> **Same-day blending, observed converging**: `marts.ambient_wind_daily_comparison`
> ([§8](#8-analytics-layer-dbt)) averages the *whole calendar day's* history,
> including readings generated before anchoring went live, so a day mixing
> old and new data reads closer to the unanchored range than the anchor
> itself. This isn't hypothetical - the day this was shipped, the fleet
> average started at 8.58 m/s (only 20 of 1,493 rows were anchored) and had
> converged to 5.02 m/s by the same evening (vs. 3.99 real weather / 4.74
> real buoy) as anchored rows came to dominate the day's average. A rolling
> window instead of a calendar-day grain would remove the lag entirely — see
> [§16](#16-roadmap--extending-this).

### Solar

Same mechanism, anchoring to `shortwave_radiation_w_m2` instead of
`wind_speed_ms`, and expressed as a cloud-cover factor rather than a direct
value (since the simulator models clear-sky irradiance as a function of
time-of-day, not a flat number):

```python
# airflow/dags/solar_etl_dag.py
def _fetch_reference_irradiance(conn) -> float | None:
    row = conn.execute(
        text(
            "SELECT shortwave_radiation_w_m2, ts FROM weather_api_readings ORDER BY ts DESC LIMIT 1"
        )
    ).fetchone()
    if row is None or row.shortwave_radiation_w_m2 is None:
        return None
    staleness = now() - row.ts
    if staleness > max_staleness:  # default 180 min
        return None
    return float(row.shortwave_radiation_w_m2)
```

```python
# src/extract/solar_simulator.py
def _initial_cloud_factor(self) -> float:
    if self._reference_irradiance_w_m2 is None or self._reference_irradiance_w_m2 <= 0:
        return self._rng.uniform(0.6, 1.0)  # unanchored fallback
    implied = self._reference_irradiance_w_m2 / PEAK_CLEAR_SKY_W_M2
    spread = self._rng.uniform(-0.1, 0.1)
    return max(0.15, min(implied + spread, 1.05))
```

**Verified effect**: triggered live while the real irradiance reading was
605.0 W/m², the fleet's irradiance landed at 421–590 W/m² (implied cloud
factor ≈ 0.64), squarely aligned with reality rather than following an
unanchored clear-sky assumption.

---

## 8. Analytics layer (dbt)

A small dbt project sits on top of the curated tables — its own Postgres
schemas (`staging`, `marts`), kept visibly separate from `public` via a
custom `generate_schema_name` macro.

```
public.* → source() → staging.stg_* (views) → ref() → marts.* (tables)
```

**Staging models**: `stg_scada_readings`, `stg_solar_readings`,
`stg_pipeline_run_audit`, `stg_weather_api_readings`, `stg_iot_buoy_readings`
— thin pass-throughs with light derivation (e.g. a synthetic `reading_key`
for native uniqueness tests without needing `dbt_utils`).

**Marts**:

| Mart | Grain | What it answers |
|---|---|---|
| `turbine_daily_summary` | turbine × day | Avg/max/min power, reading count, anomaly count, % operational, capacity factor (avg power ÷ rated 3,300 kW) |
| `solar_daily_summary` | plant × day | Same shape as above for solar: avg irradiance/DC/AC power, capacity factor (avg DC power ÷ 5,000 kWp) |
| `pipeline_run_daily_summary` | day | Run count, success rate, total rows extracted/loaded/rejected, avg/max duration — both fleets combined, since it reads the shared `pipeline_run_audit` |
| `ambient_wind_daily_comparison` | day | Fleet avg wind speed vs. real Open-Meteo vs. real NOAA buoy, joined by day — a plausibility check against independent, externally-sourced ground truth |
| `renewable_fleet_daily_summary` | day | **The payoff mart**: wind + solar total average output side by side plus a combined total — the portfolio-level view a mixed-fleet operator would actually want |

```sql
-- SELECT * FROM marts.renewable_fleet_daily_summary ORDER BY reading_date DESC LIMIT 1;
 reading_date | turbine_count | wind_total_avg_power_kw | plant_count | solar_total_avg_dc_power_kw | combined_total_avg_power_kw
--------------+---------------+--------------------------+-------------+-------------------------------+------------------------------
 2026-08-07   |            20 |                 36780.15 |           8 |                      25752.93 |                     62533.08
```

**Tests**: 27 data tests across staging and marts — `not_null`, `unique`,
and `accepted_values` on `status_code` (matching `SOLAR_VALID_STATUS_CODES`/
`VALID_STATUS_CODES` in the Python validators) and audit `status`. Full
`dbt build`: **37/37 passing** (10 models + 27 tests).

**Source freshness**: `scada_readings`/`solar_readings` also have a
`freshness` block in `_sources.yml` (`warn_after: 15 min`, `error_after: 30
min` — three and six missed 5-minute DAG cycles respectively). This catches
a failure mode none of the row-level validation in [§5](#5-data-quality-framework)
can: an absent pipeline produces zero *bad* rows, just zero rows, and
freshness is the only check here that's actually looking for silence rather
than for badly-shaped data. Run it: `dbt source freshness --profiles-dir .`

**Docs site**: `dbt docs generate` produces a self-contained static site —
an interactive lineage graph (`public.scada_readings → stg_scada_readings →
turbine_daily_summary → renewable_fleet_daily_summary`) plus a column-level
schema browser sourced from the same `description:` fields used throughout
this repo's `.yml` files. CI publishes it to GitHub Pages on every push to
`master`, alongside the full HTML reference doc — GitHub Pages serves one
artifact per deployment, so both are assembled into one directory first
(`docs/documentation.html` → site root, dbt's generated site → `/dbt-docs/`
underneath it; both are fully self-contained, so neither cares which path
it's served from):

- **Full reference doc**: https://allmamun556.github.io/pyspark-etl-toy/
- **dbt docs (lineage + schema browser)**: https://allmamun556.github.io/pyspark-etl-toy/dbt-docs/

Run it locally: `docker compose run --rm dbt build --profiles-dir .`

---

## 9. Dashboard

`dashboard/api/main.py` (FastAPI) + `dashboard/static/` (vanilla JS +
Chart.js, no build step). Queries Postgres via the same `src.db.session`/
`src.config` the pipeline uses — no separate data store, no caching layer.
Most routes read the `public` schema directly; the two `/stats` routes read
dbt's `marts.*` tables instead (see below).

| Route | Returns |
|---|---|
| `GET /api/health` | Liveness check |
| `GET /api/summary` | Wind fleet totals, latest avg power/wind, last `scada_etl_pipeline` run |
| `GET /api/turbines/latest` | One row per turbine — its newest reading |
| `GET /api/turbines/stats` | Per-turbine aggregates, from `marts.turbine_daily_summary` |
| `GET /api/turbines/{id}/timeseries` | Last *n* readings for one turbine (chart source) |
| `GET /api/anomalies` | Recent rows with `is_anomalous = true` |
| `GET /api/rejects` | Recent `scada_readings_rejects` rows |
| `GET /api/solar/summary` | Solar fleet totals, latest avg DC/AC power/irradiance, last `solar_etl_pipeline` run |
| `GET /api/solar/plants/latest` | One row per plant — its newest reading |
| `GET /api/solar/plants/stats` | Per-plant aggregates, from `marts.solar_daily_summary` |
| `GET /api/solar/plants/{id}/timeseries` | Last *n* readings for one plant (chart source) |
| `GET /api/solar/anomalies` | Recent solar rows with `is_anomalous = true` |
| `GET /api/solar/rejects` | Recent `solar_readings_rejects` rows |
| `GET /api/audit/runs` | Recent `pipeline_run_audit` rows, both fleets — `task_id` in the response is what tells them apart |
| `GET /api/external` | Latest weather (incl. `shortwave_radiation_w_m2`) + buoy reading, plus recent external DAG runs |

**Why `/stats` reads from dbt marts, not raw tables**: the per-turbine and
per-plant aggregation logic (avg/max power, anomaly counts, capacity factor)
already exists once, tested, in `dbt/models/marts/turbine_daily_summary.sql`
and `solar_daily_summary.sql` ([§8](#8-analytics-layer-dbt)). The dashboard
used to reimplement the same `GROUP BY` aggregation directly against
`scada_readings`/`solar_readings` — two independent places that could drift
out of sync with no test catching it. Reading the mart instead makes it a
single source of truth: a weighted average across each mart's daily grain
(`sum(avg_power_kw * reading_count) / sum(reading_count)`, correctly
weighting days with more readings) rather than a second, parallel
aggregation. The tradeoff is a real dependency: the dashboard's `/stats`
routes are only as fresh as the last `dbt build`, which is why
`docker-compose.yml` makes `dashboard` wait on `dbt: condition:
service_completed_successfully` rather than just `postgres: service_healthy`.

**Frontend — one wind page, one solar page (`index.html` / `solar.html`), each with four charts and two tables:**

| Panel | Type | Source |
|---|---|---|
| KPI row | 8 stat cards | `/api/summary` |
| Fleet overview | Bar (avg power per turbine) + line (anomaly count), dual-axis | `/api/turbines/stats` |
| Turbine time series | Line, dropdown-selected turbine | `/api/turbines/{id}/timeseries` |
| **Power curve** | **Scatter** — wind speed (x) vs. power (y), one point per turbine, red = anomalous | `/api/turbines/latest` |
| **Recent pipeline run health** | **Bar** (rows loaded/rejected) + **line** (duration), dual-axis, last 10 runs | `/api/audit/runs` |
| Recent data quality events | Table — merged anomalies + rejects, newest first | `/api/anomalies` + `/api/rejects` |
| External data sources | KPI cards + table | `/api/external` |

The two bolded panels replace what used to be two more raw tables ("latest
reading per turbine" and "recent pipeline runs") — a scatter plot of wind
speed against power *is* the classic wind-turbine power curve, so it's a
more physically meaningful view of the same latest-reading data than a
table of numbers, and it's where an anomalous reading (icing spike, stuck
sensor) visibly falls off the expected curve rather than needing to be
read out of a column. The pipeline-runs chart makes a duration or
rejection-rate trend across recent runs visible at a glance in a way
scanning a table of numbers doesn't. The anomalies and rejects tables were
merged into one (`type` column distinguishes them) specifically to keep the
total table count to two per page rather than four, now that two panels
converted to charts. All panels poll every 15 seconds.

Access at **http://localhost:3000** once the stack is up.

---

## 10. Deployment

Each service that needs its own dependency set gets its own Dockerfile —
kept separate specifically to avoid three different dependency conflicts
colliding in one image.

| Service | Image | Port | Why it's separate |
|---|---|---|---|
| `postgres` | timescale/timescaledb:2.17.2-pg16 | 5432 | Drop-in-compatible build on the same PostgreSQL 16 (same data dir format, same wire protocol) with the `timescaledb` extension pre-installed — not a different database. Needed for the hypertables in [§3](#3-schema-reference) |
| `airflow-webserver` / `-scheduler` / `-init` | `Dockerfile` (apache/airflow:2.10.2) | 8081 | Base image pins SQLAlchemy 1.4.x for Airflow's own ORM |
| `dashboard` | `Dockerfile.dashboard` (python:3.11-slim) | 3000 | Free to run current SQLAlchemy 2.0 + FastAPI without fighting Airflow's pin. Starts only after `dbt` completes successfully (its `/stats` routes read dbt's marts — [§9](#9-dashboard)), not just after Postgres is healthy |
| `dbt` | `Dockerfile.dbt` (python:3.11-slim) | — | Own Jinja2/click dependency graph; one-shot like `airflow-init` |

**Reproducible installs**: every `requirements*.txt` is generated from a
corresponding `requirements*.in` via `uv pip compile` (a drop-in
`pip-compile`), so every transitive dependency is pinned to an exact
version, not just the direct ones — `docker compose build` (or a fresh
`pip install -r requirements.txt`) resolves identically today and a year
from now. `apache-airflow` is deliberately excluded from the compiled set
and pinned separately at the bottom of `requirements.txt`, since Airflow
ships its own version-specific constraints file and compiling it alongside
everything else risks a resolver conflict.

**CD**: on every push to `master`, CI also builds and pushes all three
images to GitHub Container Registry — `ghcr.io/allmamun556/scada-etl-pipeline-{airflow,dashboard,dbt}`,
tagged both `:latest` and `:<commit-sha>` for traceability. PR builds still
build every image (to prove the Dockerfile works) but never push — an
unreviewed branch shouldn't be able to publish an artifact.

**Pre-commit hooks**: `pip install pre-commit && pre-commit install` runs
`ruff check --fix` and `ruff format` on every commit — the same checks CI
runs, but before a push instead of after. Since this project lives inside a
monorepo, every hook is scoped to `data_engineer_tasks/scada-etl-pipeline/`
specifically (`.pre-commit-config.yaml`'s `files:` pattern) — confirmed
necessary the hard way, since an unscoped first run reformatted 35 files
belonging to other, unrelated projects sharing the same `.git`.

```bash
git clone <your-repo-url> scada-etl-pipeline
cd scada-etl-pipeline
cp .env.example .env

# Build and start Postgres + Airflow + dashboard + dbt
docker compose up --build -d

# Airflow UI:  http://localhost:8081  (user: admin / pass: admin)
# Dashboard:   http://localhost:3000
# Unpause "scada_etl_pipeline", "solar_etl_pipeline", and "external_data_sources" to start scheduled runs
```

Run dbt models + tests against whatever's loaded so far (also runs once
automatically as part of `docker compose up`):

```bash
docker compose run --rm dbt build --profiles-dir .
```

---

## 11. Testing & benchmark

73 pure-function tests, zero live-DB or network dependency:

| File | Cases | Covers |
|---|---|---|
| `test_validation.py` | 13 | Bounds, timeliness, batch duplicate detection, completeness check (wind) |
| `test_solar_validation.py` | 11 | Same six dimensions for solar, plus the AC-can't-exceed-DC physical check |
| `test_extract.py` | 12 | Power curve shape, incremental window logic, wind-speed anchoring & determinism |
| `test_solar_extract.py` | 9 | Clear-sky curve shape, true-night-is-exactly-zero regression test, irradiance anchoring & determinism |
| `test_transform.py` | 7 | Status normalization, anomaly flagging (wind) |
| `test_solar_transform.py` | 7 | Same, for solar's sun-without-output / output-without-sun checks |
| `test_weather_api_extractor.py` | 6 | Open-Meteo response parsing (incl. `shortwave_radiation`), validation |
| `test_iot_buoy_extractor.py` | 5 | realtime2 parsing, missing-value handling, validation |
| `test_alerting.py` | 3 | Slack failure notification: no-op when unconfigured, correct payload when configured, exceptions swallowed |
| **Total** | **73** | |

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

**Coverage**: `pyproject.toml` bakes `--cov` into pytest's default
`addopts`, scoped to `extract`/`transform`/`validation`/`utils`/`config` —
not all of `src/`. `src/db` and `src/load` are deliberately excluded from
that scope: they're DB-touching code, validated by the live `airflow dags
test` run below instead of by pytest, so folding them into the same
percentage would either be permanently 0% (misleading — they *are* tested,
just differently) or require mocking a database to inflate the number
without adding real coverage. `--cov-fail-under=85` makes this a real gate,
not just a report: **currently 89%**.

On top of pytest, `airflow dags test` runs `scada_etl_pipeline` and
`solar_etl_pipeline` for real in CI ([§12](#12-cicd-github-actions)) — actual
task execution against a live database, not just DagBag/schema validation,
which is what pytest structurally can't cover for DAG wiring.

**Idempotency — `scripts/verify_idempotency.py`**: the claim, repeated
throughout this doc, that replaying a load never duplicates rows rests on
one line of SQL (`ON CONFLICT (turbine_id, ts) DO UPDATE`) — this script is
what actually exercises it against a real database instead of leaving it as
an assertion about that SQL's design. Two scenarios: (1) load the same
batch twice, assert the row count doesn't grow; (2) load two batches whose
time windows partially overlap (simulating overlapping/retried DAG runs),
assert the final count equals the deduplicated union, not the sum. Runs in
CI ([§12](#12-cicd-github-actions)) against the freshly-migrated database,
right after the Alembic step.

```bash
python scripts/verify_idempotency.py
```

**Benchmark — `scripts/benchmark.py`**: what turns "improved pipeline
efficiency by 40%" from a claim into a reproducible number. Generates
synthetic readings, times the naive row-by-row `INSERT` path against the
optimized COPY+staged-UPSERT path, prints ms/row and the throughput
multiplier. (The naive path is capped at 50,000 rows in the comparison —
run to completion at full scale, it's too slow to be worth waiting for.)
Every row it writes is prefixed `OPT-`/`NAIVE-` on the turbine id and is
deleted both before the run starts (in case a previous run crashed
mid-benchmark) and always after, via `try`/`finally` — `scada_readings` is
also the pipeline's real curated table, and leaving synthetic rows behind
would get counted as real pipeline data by the dashboard and dbt marts.

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

| Job | What it validates |
|---|---|
| `lint-and-test` | `ruff check .` + all 73 pytest cases with an 85%-coverage gate ([§11](#11-testing--benchmark)) (installs `requirements.txt` minus `apache-airflow`, since nothing under test imports it and it needs its own constraints file to install reliably) |
| `migrations-and-dbt` | Spins up a real `timescale/timescaledb:2.17.2-pg16` service container (plain `postgres:16-alpine` can't run migration `0004`, which needs the `timescaledb` extension), runs `alembic upgrade head` against it from empty, `scripts/verify_idempotency.py`, `dbt build`, `dbt source freshness` + `dbt docs generate` (published to Pages below), then installs Airflow separately and runs `airflow dags test scada_etl_pipeline` + `airflow dags test solar_etl_pipeline` against that same database — real task execution, not just schema validation |
| `docker-build` | Builds all three Dockerfiles (Airflow, dashboard, dbt) with GitHub Actions layer caching; on `master` pushes only, also pushes them to GHCR ([§10](#10-deployment)) |
| `deploy-dbt-docs` | On `master` pushes only: publishes the full HTML reference doc + the dbt docs site generated above to GitHub Pages — **https://allmamun556.github.io/pyspark-etl-toy/** (docs) and **/dbt-docs/** (lineage + schema browser) |

**Why `airflow dags test` and not just DagBag import validation**: a DAG
that merely *parses* can still be wrong in ways that only show up when a
task actually runs — an XCom key that doesn't match between push and pull,
a reference-anchoring query that's fine syntactically but returns the wrong
shape. `dags test` executes the real task callables (`extract_transform_
validate` → `load` → `update_watermarks_and_audit`) against the job's
freshly-migrated Postgres, using an isolated SQLite metadata DB and
`SequentialExecutor` (SQLite doesn't support Airflow's default
`LocalExecutor`) so it needs nothing beyond what's already in the job.

**Why `external_data_sources` is excluded from this check**: its two tasks
make real HTTP calls to Open-Meteo and NOAA NDBC. A third-party outage —
which has genuinely happened during this project's development (a live
Open-Meteo `503`, [§2](#2-data-sources)) — says nothing about whether this
codebase is correct, and a CI gate that can fail on someone else's downtime
isn't a gate worth having. `scada_etl_pipeline` and `solar_etl_pipeline`
have no such dependency: if `weather_api_readings` is empty (as it is in a
freshly-migrated CI database), reference anchoring just returns `None` and
both simulators fall back to their unanchored default — by design, not a
CI-only workaround ([§7](#7-real-data-anchoring-wind--solar)).

> **Another real gotcha, caught by the first actual CI run**: Airflow was
> first installed straight into the job's shared Python environment
> (already populated by the `dbt`/`alembic` step), and CI immediately broke
> with `ImportError: cannot import name 'Sentinel' from 'typing_extensions'`
> — pip left an already-installed, incompatible version in place instead of
> resolving to what Airflow's constraints file wanted. Isolating Airflow
> into its own virtualenv fixed that, but surfaced the *next* layer of the
> same problem: installing the pipeline's own lockfile (`sqlalchemy==2.0.35`)
> into that venv upgraded SQLAlchemy out from under Airflow's ORM models,
> which are written for 1.4's declarative style and raise `ArgumentError`
> under 2.0's stricter Annotated Declarative mapping. Fixed by excluding
> `sqlalchemy` from what's installed into the Airflow venv — the exact same
> exclusion (and reason) `Dockerfile` already uses for the production
> Airflow image. Both fixes were verified locally (isolated venv + real
> Postgres + isolated SQLite Airflow metadata) before pushing again — this
> project's whole "verify live before calling it done" pattern, applied to
> its own CI pipeline.

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
| `solar_plant_count` | 8 | Fleet size the solar simulator generates |
| `solar_capacity_kwp` | 5000.0 | Per-plant DC nameplate capacity |
| `solar_inverter_ac_capacity_kw` | 4500.0 | Per-plant AC nameplate (inverter clipping ceiling) |
| `max_irradiance_w_m2` | 1400.0 | Validation ceiling |
| `min_panel_temp_c` / `max_panel_temp_c` | -20 / 90 | Validation range |
| `max_dc_power_kw` / `max_ac_power_kw` | 5500.0 / 5000.0 | Validation ceilings (small headroom above nameplate) |
| `max_future_skew_seconds` | 300 | Timeliness check tolerance |
| `weather_api_base_url` | `api.open-meteo.com/v1/forecast` | HTTP source endpoint |
| `weather_latitude` / `weather_longitude` | 53.55 / 8.09 | Bremerhaven, DE |
| `iot_buoy_base_url` | `ndbc.noaa.gov/data/realtime2` | IoT source endpoint |
| `iot_buoy_station_id` | `46050` | Stonewall Bank, OR |
| `http_request_timeout_seconds` | 10 | Both external extractors |
| `reference_wind_max_staleness_minutes` | 180 | [§7](#7-real-data-anchoring-wind--solar) wind anchoring freshness cutoff |
| `reference_irradiance_max_staleness_minutes` | 180 | [§7](#7-real-data-anchoring-wind--solar) solar anchoring freshness cutoff |
| `slack_webhook_url` | `None` | DAG failure alerts ([§6](#6-orchestration-airflow)); unset by default, so alerting is a safe no-op out of the box |
| `log_level` | `INFO` | Structured JSON logging |

Host-only: `POSTGRES_HOST_PORT` (default 5432, in `.env` not `src/config.py`)
— overrides `docker-compose.yml`'s Postgres port mapping if 5432 is already
taken on your machine. Has no effect on `POSTGRES_PORT` above, which
containers use internally regardless.

---

## 14. Repository layout

```
scada-etl-pipeline/
├── airflow/dags/
│   ├── scada_etl_dag.py              # turbine SCADA — every 5 min
│   ├── solar_etl_dag.py              # solar PV plants — every 5 min
│   └── external_data_dag.py          # weather + buoy — every 15 min
├── src/
│   ├── config.py                     # every setting, env-driven
│   ├── extract/
│   │   ├── scada_simulator.py        # simulated SCADA feed
│   │   ├── solar_simulator.py        # simulated solar plant fleet
│   │   ├── weather_api_extractor.py  # real HTTP API: Open-Meteo
│   │   └── iot_buoy_extractor.py     # real IoT: NOAA NDBC
│   ├── transform/
│   │   ├── transformers.py           # wind: cleaning, derived metrics, anomaly flags
│   │   └── solar_transformers.py     # solar: same shape, reuses normalize_status_code
│   ├── validation/
│   │   ├── validators.py             # wind: 6 DQ dimensions
│   │   ├── solar_validators.py       # solar: same 6 dimensions
│   │   └── external_validators.py    # weather/buoy bounds
│   ├── load/
│   │   ├── loaders.py                # batch COPY + idempotent UPSERT (wind); shared record_run_audit()
│   │   ├── solar_loaders.py          # batch COPY + idempotent UPSERT (solar)
│   │   └── external_loaders.py       # single-row idempotent UPSERT
│   ├── db/{models.py, session.py}    # SQLAlchemy ORM + engine/session
│   └── utils/
│       ├── logging_config.py         # structured JSON logging
│       └── alerting.py               # Slack DAG-failure notification, safe no-op unconfigured
├── dbt/models/{staging,marts}/       # analytics models on the curated tables
├── dashboard/
│   ├── api/main.py                   # FastAPI read API (stats routes read dbt marts)
│   └── static/                       # vanilla JS + Chart.js frontend
├── docs/documentation.html           # full self-contained HTML reference doc
├── migrations/versions/              # 0001_initial_schema … 0004_timescaledb_hypertables
├── sql/init.sql                      # bootstrap DDL, mirrors Alembic
├── scripts/
│   ├── benchmark.py                  # naive vs optimized load benchmark (self-cleaning)
│   └── verify_idempotency.py         # replay + overlapping-window dedup check (self-cleaning)
├── tests/                            # 73 cases, 9 files
├── docker-compose.yml                # timescaledb + airflow + dashboard + dbt
├── Dockerfile                        # Airflow image
├── Dockerfile.dashboard              # Dashboard API image
├── Dockerfile.dbt                    # dbt image
├── .pre-commit-config.yaml           # ruff lint + format, scoped to this directory
├── pyproject.toml                    # ruff + pytest + coverage config (85% gate)
├── requirements.in / requirements-dashboard.in / requirements-dbt.in     # direct deps
├── requirements.txt / requirements-dashboard.txt / requirements-dbt.txt  # pip-compile lockfiles
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
- **Three DAGs instead of one**: an outage at NOAA or Open-Meteo is a real,
  external, unpredictable failure mode. Isolating external sources into
  their own DAG means they can retry and eventually fail on their own
  schedule without touching either simulated pipeline's SLA - and wind and
  solar are separate simulated asset classes with no reason to share a
  schedule or a blast radius either.
- **Share `pipeline_run_audit`, but not the readings tables**: wind and
  solar's audit rows are identical in shape (extract/load/reject counts,
  duration, status) so duplicating that table per fleet would just be
  drift risk. Their readings/rejects/watermark tables are genuinely
  different schemas, so those stay separate rather than forcing a
  one-size-fits-all table with a pile of nullable columns.
- **A separate image per service instead of one shared image**: Airflow's
  base image pins SQLAlchemy 1.4.x for its own ORM; the dashboard and dbt
  both want current-generation dependencies. Three Dockerfiles avoids a
  three-way dependency resolution fight inside one image.
- **TimescaleDB over partitioning by hand**: `create_hypertable()` plus
  `add_retention_policy()` gets automatic chunking and a self-cleaning
  90-day window in two lines of migration SQL, on the same PostgreSQL wire
  protocol and data format — no application code changes, no separate
  database to operate. Hand-rolled declarative partitioning would need its
  own cron job to drop old partitions; this needs none.
- **Dashboard reads dbt marts instead of re-deriving the same aggregation
  twice**: before this, `/api/turbines/stats` ran its own `GROUP BY` against
  `scada_readings` in parallel with dbt's `turbine_daily_summary` model
  computing the same thing — two implementations of one aggregation, with
  nothing to catch them drifting apart. Reading the mart makes dbt's tested
  SQL the single source of truth, at the cost of a real startup-ordering
  dependency (dashboard now waits on `dbt` completing, not just Postgres
  being up).
- **Slack alerting via a plain `on_failure_callback`, not an Airflow
  provider package**: `requests.post` to an incoming webhook is a few lines
  and one dependency already in the project; the `apache-airflow-providers-
  slack` package would add its own version-compatibility surface against
  Airflow 2.10.2 for a single notification use case. Defaults to unset
  (safe no-op) specifically so the DAGs run correctly out of the box
  without demanding a Slack workspace to test this repo.

---

## 16. Roadmap / extending this

- Swap the simulator in `src/extract/scada_simulator.py` for a real
  OPC-UA / MQTT client or a historian export — the rest of the pipeline is
  source-agnostic by construction.
- Extend `airflow dags test` in CI to cover `external_data_sources` too, by
  mocking the Open-Meteo/NOAA HTTP calls (`responses` or a fixture server)
  instead of skipping the DAG entirely — would catch wiring bugs in that
  DAG the same way [§12](#12-cicd-github-actions) now does for the other two,
  without depending on either service's real uptime.
- Wire the Slack alert path to a real workspace webhook in the deployed
  environment and confirm a forced task failure actually lands a message —
  currently verified via mocked unit tests only ([§6](#6-orchestration-airflow)).
- CI's `dbt source freshness` step only proves the config is valid, since
  the freshly-migrated CI database has no data to check freshness *of*
  ([§8](#8-analytics-layer-dbt)). The real check needs to run on a schedule
  against the live pipeline's data (e.g. a periodic GitHub Actions
  `workflow_dispatch`/cron hitting the production database, or an Airflow
  sensor task) - wiring that up would make freshness an actual alertable
  gate instead of a config smoke-test.
- GHCR images publish successfully but are **private by default** even on
  a public repo — visibility has to be flipped once, manually, in the
  repo's Packages settings before `docker pull` works for someone else.
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
- Solar's clear-sky model uses fixed UTC sunrise/sunset hours rather than
  computing actual solar position for the plant's latitude/date - swapping
  in a proper solar-position calculation (e.g. via `pvlib`) would make the
  irradiance curve accurate for a real site instead of a stylized
  approximation.
- Add a solar equivalent of `ambient_wind_daily_comparison` comparing fleet
  irradiance against `weather_api_readings.shortwave_radiation_w_m2`
  directly, the same way wind speed is checked against reality today.

---
---

# Deutsche Version

> **Hinweis**: Dies ist die deutsche Übersetzung der obigen Dokumentation.
> Code, SQL, YAML, Dateipfade, Tabellen-/Spaltennamen, Umgebungsvariablen
> und Befehle bleiben unübersetzt, da es sich um tatsächliche
> Systembezeichner handelt, nicht um englischen Fließtext. Bei
> Detailfragen ist die englische Version oben maßgeblich.

## Inhaltsverzeichnis (Deutsch)

0. [Überblick](#0-überblick-de)
1. [Architektur](#1-architektur-de)
2. [Datenquellen](#2-datenquellen-de)
3. [Schema-Referenz](#3-schema-referenz-de)
4. [Pipeline-Interna](#4-pipeline-interna-de)
5. [Datenqualitäts-Framework](#5-datenqualitäts-framework-de)
6. [Orchestrierung (Airflow)](#6-orchestrierung-airflow-de)
7. [Anbindung an echte Daten (Wind + Solar)](#7-anbindung-an-echte-daten-wind--solar-de)
8. [Analyseschicht (dbt)](#8-analyseschicht-dbt-de)
9. [Dashboard](#9-dashboard-de)
10. [Deployment](#10-deployment-de)
11. [Tests & Benchmark](#11-tests--benchmark-de)
12. [CI/CD (GitHub Actions)](#12-cicd-github-actions-de)
13. [Konfigurationsreferenz](#13-konfigurationsreferenz-de)
14. [Repository-Struktur](#14-repository-struktur-de)
15. [Design-Entscheidungen](#15-design-entscheidungen-de)
16. [Roadmap / Erweiterungen](#16-roadmap--erweiterungen-de)

---

## 0. Überblick <a name="0-überblick-de"></a>

### Problemstellung

Stellenausschreibungen und Lebensläufe im Data-Engineering enthalten
regelmäßig Sätze wie *"Entwarf und optimierte ETL-Pipelines für die
großskalige Datenaufnahme und -transformation von SCADA- und
Zeitreihendaten und verbesserte die Pipeline-Effizienz um 40 %."* Dieser
Satz ist in dieser Form nicht überprüfbar — es gibt keinen Code zum
Nachlesen, keine Zahl zum Nachvollziehen, und keine Möglichkeit
festzustellen, ob die "40 %" aus einer echten Messung stammen. Echte
SCADA-Telemetriedaten einzelner Windturbinen sind zudem Eigentum der
Windpark-Betreiber und werden nirgendwo offen veröffentlicht — ein
Portfolio-Projekt in diesem Bereich kann also nicht einfach, wie bei
Einzelhandelsdaten möglich, einen öffentlichen Datensatz herunterladen.
Die Daten müssen selbst erzeugt werden, nicht nur verarbeitet.

Das Problem, das dieses Projekt löst: **ein produktionsreif gestaltetes
SCADA-/Zeitreihen-ETL-System von Anfang bis Ende bauen, bei dem jede
Behauptung, die ein solcher Lebenslaufsatz aufstellen würde, durch
lauffähigen Code und eine reproduzierbare Zahl belegt ist** — keine
Behauptung, kein Screenshot, kein Spielzeugskript, das nur den
Erfolgsfall behandelt.

### Ziele

1. **Eine realistische Datenerfassungsdomäne nachbilden**, ohne Zugang zu
   echter Hardware — ein physikalisch modellierter Windturbinen-Simulator
   und ein zweiter, unabhängiger Solar-PV-Anlagen-Simulator, beide mit
   echter Fehlerinjektion (festhängende Sensorwerte, Ausreißer-Spitzen),
   damit die Datenqualitätsschicht echte Arbeit zu leisten hat.
2. **Die Simulation in der Realität verankern**, statt sie auf reinem
   Rauschen driften zu lassen — beide simulierten Flotten werden an echte,
   live abrufbare, kostenlose externe Daten angebunden (siehe [§7](#7-anbindung-an-echte-daten-wind--solar-de)).
3. **Den Durchsatz-Anspruch belegen, nicht nur behaupten** — ein
   reproduzierbarer Benchmark, der einen naiven Zeile-für-Zeile-Ladepfad
   gegen einen optimierten Batch-Pfad misst, mit einer echten Zahl statt
   einer Behauptung ([§11](#11-tests--benchmark-de)).
4. **Die Belange einer echten Produktionspipeline einbauen**, die ein
   Spielzeugskript nicht hat: idempotente Wiederherstellung nach
   Wiederholungen und überlappenden Zeitfenstern, Datenqualitäts-Gates vor
   den kuratierten Tabellen, Beobachtbarkeit (strukturierte Logs,
   Audit-Tabellen, Slack-Benachrichtigungen), begrenztes Speicherwachstum
   (Aufbewahrungsrichtlinien) und eine CI, die die Pipeline tatsächlich
   ausführt statt sie nur zu linten.
5. **Alles vollständig einsehbar und lauffähig machen** — ein einziges
   `docker compose up --build -d` bringt den gesamten Stack hoch, und
   jede Designentscheidung ist mit ihrer Begründung dokumentiert, nicht
   nur mit dem Was.

### Methodik

- **Geschichtete Architektur statt Monolith**: `extract/` → `transform/`
  → `validation/` → `load/` sind unabhängige, einzeln testbare Module ohne
  gegenseitige Imports interner Details ([§1](#1-architektur-de), [§4](#4-pipeline-interna-de)).
- **Ehrlich simulieren**: jeder simulierte Wert entsteht aus einem
  expliziten physikalischen Modell (kubische Windleistungskurve,
  Klarhimmel-Solarkurve, NOCT-Panel-Erwärmung) mit dokumentierten
  Vereinfachungen — keine Blackbox ([§2](#2-datenquellen-de)).
- **Mit Airflow orchestrieren, nicht mit Cron**: drei DAGs, Wiederholungen
  mit exponentiellem Backoff, SLA-Überwachung, Fehlerbenachrichtigung ([§6](#6-orchestrierung-airflow-de)).
- **Bei jedem Schritt live verifizieren**: jede Änderung wurde während
  der Entwicklung gegen ein echtes laufendes System (echtes Postgres,
  echter Airflow-Scheduler, echter CI-Lauf) geprüft, bevor sie als
  abgeschlossen galt — dabei wurden reale Fehler gefunden und behoben, die
  ein rein lokaler Workflow ohne Live-Verifikation stillschweigend
  ausgeliefert hätte (dokumentiert in [§12](#12-cicd-github-actions-de)).
- **Mit pytest testen, was pytest erreichen kann; gegen eine echte
  Datenbank testen, was eine echte Datenbank braucht**: 73
  reine-Funktions-Unittests für Extract/Transform/Validation-Logik, plus
  separate Live-Datenbank-Checks (`airflow dags test`,
  `scripts/verify_idempotency.py`, `dbt build`) für alles, was
  tatsächlich eine Datenbank benötigt — statt eine Datenbank zu mocken, um
  eine Coverage-Zahl aufzublähen ([§11](#11-tests--benchmark-de)).
- **Das Warum dokumentieren, nicht nur das Was**: jede nicht offensichtliche
  Entscheidung nennt den Kompromiss, gegen den sie abgewogen wurde ([§15](#15-design-entscheidungen-de)),
  und echte Vorfälle während der Entwicklung werden dokumentiert statt
  verschwiegen.

### Ergebnisse

| Metrik | Ergebnis |
|---|---|
| Unit-Tests | 73/73 bestanden, 89 % Testabdeckung der abgedeckten Module (85 %-CI-Schwelle) |
| dbt-Tests | 37/37 bestanden (10 Modelle + 27 Datentests) |
| Live-DAG-Ausführung in CI | `scada_etl_pipeline` und `solar_etl_pipeline` laufen bei jedem Push vollständig gegen eine echte Datenbank |
| Idempotenz | Gegen eine echte Datenbank verifiziert, nicht nur behauptet — sowohl Wiederholungs- als auch Überlappungsszenarien bestehen ([§11](#11-tests--benchmark-de)) |
| Benchmark | Naives Zeile-für-Zeile-`INSERT` vs. optimiertes COPY+staged-UPSERT, selbst reproduzierbar mit `python scripts/benchmark.py` |
| Datenquellen | 2 echte, live, kostenlose externe Quellen; 2 simulierte Flotten daran verankert, nicht auf Rauschen driftend |
| CI/CD | 4 Jobs (Lint+Coverage, Migrationen+dbt+DAG-Ausführung, Docker-Build+GHCR-Push, Pages-Deploy), bei jedem Push grün |
| Live-Artefakte | Dashboard (2 Seiten, je 4 Diagramme + 2 Tabellen), dbt-Docs-Site auf GitHub Pages, Docker-Images auf GHCR |
| Während der Entwicklung gefundene und behobene reale Vorfälle | Ein CI-Abhängigkeitskonflikt (`typing_extensions`/`sqlalchemy` vs. Airflow), ein per isoliertem Nachtest widerlegter falscher XCom-Alarm, sowie eine versehentliche monorepo-weite Neuformatierung, die vor dem Commit abgefangen und rückgängig gemacht wurde — alles dokumentiert statt verschwiegen ([§12](#12-cicd-github-actions-de)) |

Das System erfasst Windturbinen-SCADA- und Solar-PV-Anlagendaten jeweils
im 5-Minuten-Takt, validiert sie gegen physikalische und statistische
Regeln, **bevor** sie die kuratierten Tabellen erreichen, und lädt sie
idempotent mit Batch-Durchsatz. Ein dritter, unabhängiger DAG holt alle 15
Minuten echte Umgebungswetter- und Ozeanboje-Telemetrie ein — einerseits,
um beiden simulierten Flotten etwas Externes und Wahres zu geben, an dem
sie sich selbst überprüfen können, andererseits (seit [§7](#7-anbindung-an-echte-daten-wind--solar-de))
um ihre Ausgabe daran zu verankern. dbt verwandelt die kuratierten
Tabellen in getestete Analyse-Marts; ein kleines Dashboard macht den
Zustand und die Ergebnisse des gesamten Systems ohne SQL-Client sichtbar.

**Vier Quellen speisen das Warehouse**: zwei physikalisch-realistische
simulierte Flotten (Windturbinen und Solar-PV-Anlagen) plus zwei
**echte, live, kostenlose** externe Quellen ohne API-Schlüssel — die
**Open-Meteo-HTTP-API** (Umgebungswetter + Solarstrahlung) und eine
**NOAA-NDBC-Ozeanboje** (echte IoT-Hardware). Beide simulierten Flotten
verankern sich an den echten Quellen, statt auf reinem Rauschen zu
driften.

Beispielausgabe einer laufenden Instanz (Ihre wird abweichen — dies sind
Beispielwerte, keine dauerhaften Fakten):

```text
scada_readings:  22.306 Zeilen  (20 Turbinen)
solar_readings:      72 Zeilen  (8 Anlagen)
rejects (Wind):      54 Zeilen
weather_api_readings: 20 Zeilen (inkl. echtem shortwave_radiation_w_m2)
iot_buoy_readings:    19 Zeilen
pytest:              73 / 73 bestanden
```

---

## 1. Architektur <a name="1-architektur-de"></a>

Das vollständige ASCII-Architekturdiagramm mit allen Tabellen- und
Servicebezeichnern befindet sich in [§1 der englischen Version](#1-architecture)
oben (Bezeichner wie `scada_etl_pipeline`, `TimescaleDB`, `marts.*` sind
Systemnamen und bleiben identisch). Zusammengefasst: drei unabhängige
Airflow-DAGs schreiben in eine TimescaleDB-Instanz. dbt liest die
kuratierten Tabellen in getestete Analyse-Marts; das Dashboard liest für
seine Kennzahlen die Marts und für alles andere direkt die kuratierten
Tabellen. Nichts außer den DAGs schreibt in die Datenbank, und nichts
außer der Datenbank ist gemeinsamer Zustand zwischen ihnen.

**Angewandte Designprinzipien:**

| Prinzip | Umsetzung |
|---|---|
| Trennung der Zuständigkeiten | `extract/`, `transform/`, `validation/`, `load/` sind unabhängige, einzeln testbare Module ohne gegenseitige interne Imports |
| Idempotenz | Jeder Ladepfad ist ein `INSERT ... ON CONFLICT ... DO UPDATE`, sodass ein wiederholter DAG-Lauf konvergiert statt zu duplizieren |
| Inkrementelle Extraktion | Beide simulierten Flotten führen pro Anlage einen Hochwasserstand (`extraction_watermark` / `solar_extraction_watermark`); jeder Lauf erzeugt nur Daten seit dieser Marke |
| Datenqualität als erstklassiger Schritt | Sechs Dimensionen werden vor dem Laden geprüft — siehe [§5](#5-datenqualitäts-framework-de). Fehlgeschlagene Zeilen landen mit Begründung in Reject-Tabellen, nie stillschweigend verworfen |
| Entkoppelte Fehlerdomänen | Der externe-Quellen-DAG ist getrennt von beiden simulierten Flotten-DAGs, damit ein Ausfall bei NOAA/Open-Meteo keine der beiden Pipelines mit Wiederholungsversuchen überflutet |
| Beobachtbarkeit | Strukturiertes JSON-Logging, zwei Audit-Tabellen, Airflow-SLAs + exponentielles Backoff, Slack-Fehlerbenachrichtigungen (sicherer No-Op ohne Konfiguration) |
| Konfiguration als Code | Jeder Schwellenwert, jede URL, jede Zugangsdaten ist ein `pydantic-settings`-Feld in `src/config.py`, überschreibbar per Umgebungsvariable |
| Schema-Migrationen | Alembic ist die Quelle der Wahrheit für das Schema; `sql/init.sql` spiegelt es für ein abhängigkeitsfreies lokales Bootstrap |
| Begrenztes Speicherwachstum | `scada_readings`/`solar_readings` sind TimescaleDB-Hypertables mit 90-Tage-Aufbewahrungsrichtlinie |
| Single Source of Truth für Aggregate | Die Dashboard-Statistiken pro Turbine/Anlage lesen dbts `marts.*`-Tabellen statt dieselbe Aggregations-SQL doppelt zu implementieren |
| Reproduzierbarkeit | `docker compose up --build -d` startet alle drei DAGs, das Dashboard und einen Einmal-dbt-Build ohne manuelle Schritte; jede Abhängigkeit ist über eine `pip-compile`-Lockdatei fixiert; CI veröffentlicht gebaute Images bei jedem `master`-Push auf GHCR |
| Testbarkeit | 73 pytest-Fälle (89 % Abdeckung, 85 %-Gate); `airflow dags test` führt die echten DAGs Ende-zu-Ende in CI aus; `scripts/verify_idempotency.py` belegt den Upsert-Anspruch gegen eine echte Datenbank |

---

## 2. Datenquellen <a name="2-datenquellen-de"></a>

### SCADA-Simulator — simuliert

`src/extract/scada_simulator.py` ist das einzige Modul im Code, das weiß,
"wie Daten ins System gelangen" — nichts nachgelagert erzeugt oder
erfindet Daten, was den Simulator austauschbar macht gegen einen echten
OPC-UA-/MQTT-Client, ohne sonst etwas anzufassen.

- **Leistungskurve**: kubische Rampe zwischen Einschaltgeschwindigkeit
  (3 m/s) und Nenngeschwindigkeit (12 m/s), Nennleistung (3.300 kW) bis
  zur Abschaltgeschwindigkeit (25 m/s), darüber null.
- **Winddrift**: Ornstein-Uhlenbeck-artiges Rauschen pro Turbine und Tick
  (±0,4 m/s Schritt, begrenzt auf `[0, 28]`).
- **Injizierte Fehler (~0,5 % der Ticks)**: ein "festhängender Sensor",
  der 2–5 Ticks lang den letzten Wert wiederholt (Kommunikationsstörung),
  und eine Leistungsspitze außerhalb des gültigen Bereichs, 1,2–1,8-fach
  der Nennleistung (vereisungsbedingter Anemometerfehler).
- **Referenzwind-Verankerung**: seit [§7](#7-anbindung-an-echte-daten-wind--solar-de)
  wird die Windgeschwindigkeit der Flotte pro Lauf an die letzte echte
  Open-Meteo-Messung verankert statt gleichverteilt aus `[4, 14]` gezogen.

### Solar-Anlagen-Simulator — simuliert

`src/extract/solar_simulator.py` — gleiche Begründung und Form wie der
Wind-Simulator; simuliert eine Flotte von 8 PV-Anlagen (je 5 MWp DC /
4,5 MW AC). Klarhimmel-Strahlungsmodell, NOCT-Panel-Erwärmung,
Temperatur-Derating, Wechselrichter-Clipping, echte Null in der Nacht
(kein rauschbedingter Beinahe-Null-Wert), injizierte Fehler
(festhängender Strahlungssensor, Wechselrichter-Ausfall).

### Open-Meteo — echt, HTTP-API

`src/extract/weather_api_extractor.py` — ein einfaches HTTP-GET, keine
Authentifizierung, aufgeteilt in `fetch_current_weather_raw()` (Netzwerk)
und `parse_current_weather()` (rein), damit Tests den Parser gegen eine
feste JSON-Fixture prüfen, ohne das Netzwerk zu berühren. Abfrageort:
Bremerhaven, Deutschland (echter Nordsee-Windenergie-Standort).
`shortwave_radiation` ist das Feld, das den Solar-Simulator verankert —
ein einziger HTTP-Abruf speist die Referenzwerte beider Pipelines.

### NOAA-NDBC-Boje 46050 — echt, IoT

`src/extract/iot_buoy_extractor.py` — ruft NOAAs `realtime2`-Textfeed ab
und parst die neueste (erste) Datenzeile. `MM` markiert einen fehlenden
Sensorwert und wird zu `None`, nie zu Null geparst.

Beide echten Extraktoren laufen in ihrem eigenen DAG
(`external_data_sources`), getrennt von `scada_etl_pipeline` und
`solar_etl_pipeline`, damit ein Ausfall bei NOAA oder Open-Meteo keine
der simulierten Pipelines mit Wiederholungen überflutet. Das ist keine
Theorie: während der Entwicklung lieferte Open-Meteo einen echten
`503 Service Unavailable` — der DAG erfasste `status="failed"` korrekt
(0 geladene Zeilen, kein falscher Erfolg), und Airflows eigener
Wiederholungsmechanismus griff automatisch.

---

## 3. Schema-Referenz <a name="3-schema-referenz-de"></a>

Dreizehn Tabellen im `public`-Schema, verwaltet von Alembic
(`migrations/versions/0001` bis `0004`), gespiegelt in `sql/init.sql`.
Tabellen-, Spalten- und Constraint-Namen bleiben unübersetzt (echte
Systembezeichner) — Details siehe [§3 der englischen Version](#3-schema-reference).

Zusammengefasst:

- **`scada_readings`** — kuratiert, eine Zeile pro Turbine und Zeitstempel.
  **TimescaleDB-Hypertable**, automatisch nach `ts` partitioniert, mit
  90-Tage-Aufbewahrungsrichtlinie. Zusammengesetzter Primärschlüssel
  `(id, ts)`, da TimescaleDB verlangt, dass jeder Unique-Index/Primärschlüssel
  auf einer Hypertable die Partitionierungsspalte enthält. Unique auf
  `(turbine_id, ts)` — das macht den Upsert idempotent.
- **`solar_readings`** — ebenfalls eine Hypertable, identische Logik wie
  oben, für Solaranlagen statt Turbinen.
- **`scada_readings_rejects` / `solar_readings_rejects`** — Zeilen, die
  die Validierung nicht bestanden haben, mit lesbarer Begründung.
- **`extraction_watermark` / `solar_extraction_watermark`** — Hochwasserstand
  pro Anlage für die inkrementelle Extraktion.
- **`pipeline_run_audit`** — eine Zeile pro `scada_etl_pipeline`- **oder**
  `solar_etl_pipeline`-Lauf, gemeinsam genutzt von beiden Flotten (gleiche
  Form, `task_id` unterscheidet).
- **`external_data_run_audit`** — spiegelt `pipeline_run_audit` für den
  externen-Quellen-DAG.
- **`weather_api_readings`** (echt) — unique auf `(latitude, longitude, ts)`,
  inkl. `shortwave_radiation_w_m2`.
- **`iot_buoy_readings`** (echt) — unique auf `(station_id, ts)`.

---

## 4. Pipeline-Interna <a name="4-pipeline-interna-de"></a>

Vier unabhängige, so weit wie möglich reine Schichten. Nur `extract` und
`load` haben I/O; `transform` und `validation` sind reine Funktionen über
Dataclasses.

```
RawScadaReading → transform_reading() → TransformedReading
                 → validate_batch() → valid[] / failed[]
                 → load_batch_optimized() → scada_readings
```

**Transform — `src/transform/transformers.py`**: `normalize_status_code()`
(Kleinschreibung, Trimmen, Leerzeichen zu Unterstrichen — defensiv gegen
uneinheitliche Herstellerbezeichnungen), `flag_statistical_anomaly()`
(Kreuzfeld-Konsistenzprüfung: Leistung ohne Rotation oder Rotation ohne
Leistung ist physikalisch inkonsistent, auch wenn jedes Feld einzeln im
gültigen Bereich liegt), `transform_reading()` (reine Abbildung,
Großschreibung der Turbinen-ID, Zeitstempel).

**Load — `src/load/loaders.py`**: `load_batch_optimized()` ist der
Durchsatzpfad, den der Benchmark in [§11](#11-tests--benchmark-de) misst
— COPY in eine UNLOGGED-Staging-Tabelle, dann ein einziges
`INSERT ... SELECT ... ON CONFLICT ... DO UPDATE` in einer Transaktion,
dann TRUNCATE der Staging-Tabelle. `load_batch_naive()` existiert nur,
damit `scripts/benchmark.py` etwas zum Vergleichen hat — die
Produktions-DAG ruft sie nie auf.

**Solar-Flotte** — `solar_transformers.py` / `solar_validators.py` /
`solar_loaders.py`: strukturell identisch zum Windpfad oben,
wiederverwendet `normalize_status_code()`, da die Statuscode-Bereinigung
nicht quellenspezifisch ist.

---

## 5. Datenqualitäts-Framework <a name="5-datenqualitäts-framework-de"></a>

Jede der folgenden Dimensionen wird in `src/validation/validators.py`
(SCADA), `solar_validators.py` (Solar) oder `external_validators.py`
(Wetter/Boje) durchgesetzt. Jeder Fehler auf Zeilenebene landet mit
konkreter Begründung in einer Reject-Tabelle, nie stillschweigend
verworfen.

| Dimension | Prüfung |
|---|---|
| Gültigkeit / Genauigkeit | Physikalische Grenzwerte: Windgeschwindigkeit, Leistung, Rotor-RPM, Gondeltemperatur, Pitch-Winkel — jeweils gegen einen konfigurierbaren Maximalwert |
| Konsistenz | Kreuzfeld-Prüfung: Leistung bei nahezu null Rotation, oder Rotation bei null Leistung, schlägt fehl, obwohl jedes Feld einzeln im gültigen Bereich liegt |
| Aktualität | Ein Zeitstempel mehr als `max_future_skew_seconds` (Standard 300 s) in der Zukunft wird als fehlerhafte Sensoruhr abgelehnt |
| Eindeutigkeit | `find_batch_duplicates()` erkennt `(turbine_id, ts)`-Kollisionen innerhalb eines einzelnen Extraktions-Batches |
| Vollständigkeit | `check_batch_completeness()` berechnet die erwartete Zeilenzahl aus Zeitfenster × Turbinenzahl × Intervall und protokolliert eine strukturierte Warnung bei Abweichung |
| Schema / Pflichtfelder | Fehlende `turbine_id`, fehlendes `ts` oder unbekannter `status_code` schlagen explizit fehl |

---

## 6. Orchestrierung (Airflow) <a name="6-orchestrierung-airflow-de"></a>

Drei DAGs, zwei Taktungen, drei Fehlerdomänen — bewusst getrennt, damit
ein Ausfall in einem vorgelagerten System nicht den Zeitplan eines
anderen DAGs mit Wiederholungen überflutet.

- **`scada_etl_pipeline`** — alle 5 Minuten. Aufgabengraph:
  `extract_transform_validate` → `load` → `update_watermarks_and_audit`.
- **`solar_etl_pipeline`** — alle 5 Minuten, strukturell identisch, mit
  `solar_extraction_watermark` statt `extraction_watermark`.
- **`external_data_sources`** — alle 15 Minuten, zwei unabhängige
  Aufgaben (`extract_load_weather`, `extract_load_buoy`).

**Gemeinsame Wiederholungsrichtlinie**: `retries: 3`, `retry_delay: 2 Min`,
exponentielles Backoff, `max_retry_delay: 15 Min`, `max_active_runs: 1`
pro DAG, `catchup: False`.

**Fehlerbenachrichtigung**: alle drei DAGs setzen
`on_failure_callback: notify_dag_failure` (`src/utils/alerting.py`). Bei
erschöpften Wiederholungen wird die DAG-ID, Task-ID, Lauf-ID und die
Airflow-Log-URL an einen Slack-Incoming-Webhook gesendet. Ohne
`SLACK_WEBHOOK_URL` (Standard) ist dies ein sicherer No-Op, protokolliert
auf `INFO`-Ebene, kein Absturz.

---

## 7. Anbindung an echte Daten (Wind + Solar) <a name="7-anbindung-an-echte-daten-wind--solar-de"></a>

Keiner der beiden Simulatoren liegt zufällig im selben Bereich wie die
echten Quellen — jeder Lauf liest den letzten passenden echten Wert aus
Postgres zurück und verankert seine Flotte daran.

**Wind**: `_fetch_reference_wind_speed(conn)` liest die neueste Zeile aus
`weather_api_readings`. Ist sie leer oder älter als
`reference_wind_max_staleness_minutes` (Standard 180 Min), liefert die
Funktion `None`, und der Simulator fällt auf sein ursprüngliches,
unverankertes Verhalten zurück — die beiden DAGs bleiben vollständig
entkoppelt.

**Verifizierter Effekt**: live ausgelöst bei einer echten Wettermessung
von 3,77 m/s landeten neue SCADA-Messwerte bei 1,75–6,04 m/s
(Mittelwert 3,65), gegenüber dem alten unverankerten Bereich von 4–14 m/s.

**Solar**: derselbe Mechanismus, verankert an
`shortwave_radiation_w_m2` statt `wind_speed_ms`, ausgedrückt als
Bewölkungsfaktor statt als Direktwert.

---

## 8. Analyseschicht (dbt) <a name="8-analyseschicht-dbt-de"></a>

Ein kleines dbt-Projekt auf den kuratierten Tabellen — eigene
Postgres-Schemas (`staging`, `marts`), sichtbar getrennt von `public`.

```
public.* → source() → staging.stg_* (Views) → ref() → marts.* (Tabellen)
```

**Marts**: `turbine_daily_summary`, `solar_daily_summary`,
`pipeline_run_daily_summary`, `ambient_wind_daily_comparison`,
`renewable_fleet_daily_summary` (der Auszahlungs-Mart: Wind- und
Solar-Gesamtdurchschnittsleistung nebeneinander plus Gesamtsumme).

**Tests**: 27 Datentests über Staging und Marts. Vollständiger
`dbt build`: **37/37 bestanden** (10 Modelle + 27 Tests).

**Quellenaktualität**: `scada_readings`/`solar_readings` tragen einen
`freshness`-Block (`warn_after: 15 Min`, `error_after: 30 Min`) — erkennt
"die Pipeline ist stillschweigend stehengeblieben", eine Fehlerart, die
zeilenbasierte Validierung strukturell nicht erkennen kann.

**Docs-Site**: `dbt docs generate` erzeugt eine eigenständige statische
Site — ein interaktiver Lineage-Graph plus ein spaltenweiser
Schema-Browser. Live veröffentlicht: **https://allmamun556.github.io/pyspark-etl-toy/dbt-docs/**

---

## 9. Dashboard <a name="9-dashboard-de"></a>

`dashboard/api/main.py` (FastAPI) + `dashboard/static/` (Vanilla JS +
Chart.js, kein Build-Schritt). Die meisten Routen lesen direkt das
`public`-Schema; die beiden `/stats`-Routen lesen stattdessen dbts
`marts.*`-Tabellen — eine einzige Quelle der Wahrheit statt einer zweiten,
parallelen Aggregation.

**Frontend — je vier Diagramme, zwei Tabellen, pro Flottenseite**:

- KPI-Zeile, Flottenübersicht (Balken + Linie), Zeitreihe pro Turbine/Anlage
- **Leistungskurve (Streudiagramm)** — Windgeschwindigkeit/Strahlung vs.
  Leistung, ein Punkt pro Anlage, rot = anomal. Ersetzt eine frühere
  "letzter Messwert pro Turbine"-Tabelle: ein Streudiagramm dieser beiden
  Felder **ist** die klassische Windturbinen-Leistungskurve.
- **Pipeline-Lauf-Gesundheit (Balken + Linie)** — geladene/abgelehnte
  Zeilen pro Lauf plus Laufdauer, letzte 10 Läufe.
- **Datenqualitätsereignisse** (Tabelle) — Anomalien und Rejects in einer
  Tabelle zusammengeführt (Spalte `type` unterscheidet), damit insgesamt
  nur zwei Tabellen pro Seite bleiben statt vier.
- **Externe Datenquellen** — KPI-Karten + Tabelle der letzten Läufe.

Erreichbar unter **http://localhost:3000** sobald der Stack läuft.

---

## 10. Deployment <a name="10-deployment-de"></a>

Jeder Service mit eigenem Abhängigkeitsbaum bekommt sein eigenes
Dockerfile. `postgres` läuft als `timescale/timescaledb:2.17.2-pg16`
(kompatibler Ersatz für PostgreSQL 16 mit vorinstallierter
`timescaledb`-Erweiterung). `dashboard` startet erst, nachdem `dbt`
erfolgreich durchgelaufen ist, nicht nur, wenn Postgres gesund ist.

**Reproduzierbare Installationen**: jede `requirements*.txt` wird per
`uv pip compile` aus einer `requirements*.in` erzeugt — jede transitive
Abhängigkeit ist exakt fixiert.

**CD**: bei jedem Push auf `master` baut und veröffentlicht CI außerdem
alle drei Images auf GitHub Container Registry
(`ghcr.io/allmamun556/scada-etl-pipeline-{airflow,dashboard,dbt}`),
getaggt mit `:latest` und `:<commit-sha>`.

**Pre-Commit-Hooks**: `pip install pre-commit && pre-commit install`
führt bei jedem Commit dieselben Prüfungen aus wie CI (`ruff check`,
`ruff format`) — lokal skopiert auf dieses Verzeichnis, da es sich um ein
Monorepo handelt.

```bash
git clone <ihre-repo-url> scada-etl-pipeline
cd scada-etl-pipeline
cp .env.example .env
docker compose up --build -d
```

---

## 11. Tests & Benchmark <a name="11-tests--benchmark-de"></a>

73 reine-Funktions-Tests, keine Live-Datenbank- oder Netzwerkabhängigkeit
— siehe [§11 der englischen Version](#11-testing--benchmark) für die
Aufschlüsselung nach Datei. **Testabdeckung**: `pyproject.toml` bindet
`--cov` in pytests Standard-`addopts` ein, skopiert auf die reinen
Module (`extract`/`transform`/`validation`/`utils`/`config`) — `src/db`
und `src/load` sind bewusst ausgenommen, da sie durch den Live-Lauf von
`airflow dags test` statt durch pytest validiert werden.
`--cov-fail-under=85` macht dies zu einem echten Gate: **aktuell 89 %**.

**Idempotenz — `scripts/verify_idempotency.py`**: die überall in dieser
Dokumentation wiederholte Behauptung, dass ein wiederholter Ladevorgang
nie Zeilen dupliziert, beruht auf einer Zeile SQL
(`ON CONFLICT (turbine_id, ts) DO UPDATE`) — dieses Skript überprüft sie
tatsächlich gegen eine echte Datenbank statt sie als Designannahme stehen
zu lassen.

**Benchmark — `scripts/benchmark.py`**: das, was "40 % Effizienzsteigerung"
von einer Behauptung zu einer reproduzierbaren Zahl macht. Erzeugt
synthetische Messwerte, misst den naiven Zeile-für-Zeile-`INSERT`-Pfad
gegen den optimierten COPY+staged-UPSERT-Pfad.

---

## 12. CI/CD (GitHub Actions) <a name="12-cicd-github-actions-de"></a>

Live unter [github.com/allmamun556/pyspark-etl-toy/actions](https://github.com/allmamun556/pyspark-etl-toy/actions)
— `.github/workflows/scada-etl-pipeline-ci.yml`.

> **Eine echte Monorepo-Falle**: GitHub Actions entdeckt Workflow-Dateien
> nur relativ zum **echten Repository-Root**. Die Workflow-Datei muss am
> Root des Monorepos liegen, mit `paths:`-Filter, damit sie nur bei
> Änderungen unter `data_engineer_tasks/scada-etl-pipeline/**` auslöst.

**Vier Jobs**: `lint-and-test` (Ruff + 73 pytest-Fälle mit 85 %-Coverage-Gate),
`migrations-and-dbt` (echtes TimescaleDB, Alembic-Migration,
Idempotenz-Check, `dbt build`, Quellenaktualität, `dbt docs generate`,
isolierte Airflow-Venv, `airflow dags test` für beide simulierten DAGs),
`docker-build` (alle drei Images bauen; bei `master`-Pushes zusätzlich
GHCR-Push), `deploy-dbt-docs` (bei `master`-Pushes: veröffentlicht diese
volle Dokumentation **und** die dbt-Docs-Site gemeinsam auf GitHub Pages
— siehe unten).

> **Ein weiterer echter Vorfall, gefangen vom ersten echten CI-Lauf**:
> Airflow wurde zunächst direkt in die gemeinsame Python-Umgebung des
> Jobs installiert (bereits durch den dbt/alembic-Schritt befüllt), und
> CI brach sofort mit `ImportError: cannot import name 'Sentinel' from
> 'typing_extensions'` ab — pip beließ eine bereits installierte,
> inkompatible Version, statt die von Airflows Constraints-Datei
> gewünschte Version zu verwenden. Die Isolierung von Airflow in eine
> eigene virtuelle Umgebung behob dies, brachte aber die nächste Schicht
> desselben Problems zutage: die Installation des eigenen Lockfiles der
> Pipeline (`sqlalchemy==2.0.35`) in diese Umgebung hob SQLAlchemy unter
> Airflows eigenen ORM-Modellen an, die für den deklarativen Stil von 1.4
> geschrieben sind. Behoben durch Ausschluss von `sqlalchemy` aus der
> Airflow-Venv-Installation — dieselbe Ausnahme, die `Dockerfile` bereits
> für das Produktions-Airflow-Image verwendet. Beide Fixes wurden lokal
> verifiziert, bevor erneut gepusht wurde.

**Veröffentlichte Doku**: GitHub Pages liefert genau ein Artefakt pro
Deployment — CI stellt daher diese Dokumentation (als `index.html`) und
die dbt-Docs-Site (unter `/dbt-docs/`) vor der Veröffentlichung in ein
gemeinsames Verzeichnis:

- Vollständige Dokumentation: **https://allmamun556.github.io/pyspark-etl-toy/**
- dbt-Docs (Lineage + Schema-Browser): **https://allmamun556.github.io/pyspark-etl-toy/dbt-docs/**

---

## 13. Konfigurationsreferenz <a name="13-konfigurationsreferenz-de"></a>

`src/config.py` — eine einzige `pydantic-settings`-Klasse, gecacht mit
`@lru_cache`, liest aus Umgebungsvariablen oder einer lokalen `.env`.
Enthält u. a. Verbindungsdaten, Flottengrößen (`turbine_count`,
`solar_plant_count`), Validierungsschwellenwerte für beide Flotten,
externe Quellen-Endpunkte, Anker-Frische-Schwellenwerte
(`reference_wind_max_staleness_minutes`,
`reference_irradiance_max_staleness_minutes`), `slack_webhook_url`
(Standard `None` — sicherer No-Op) und `log_level`. Vollständige Liste:
[§13 der englischen Version](#13-configuration-reference).

---

## 14. Repository-Struktur <a name="14-repository-struktur-de"></a>

Dateipfade und Namen bleiben unübersetzt (echte Systembezeichner) —
vollständiger Baum in [§14 der englischen Version](#14-repository-layout).
Wichtig: die Workflow-Datei
`.github/workflows/scada-etl-pipeline-ci.yml` liegt am echten
Git-Repository-Root, eine Ebene über diesem Projekt, nicht in diesem
Verzeichnisbaum.

---

## 15. Design-Entscheidungen <a name="15-design-entscheidungen-de"></a>

- **Airflow statt Cron**: Wiederholungen mit Backoff, SLA-Alarmierung,
  Backfill-Unterstützung und ein visueller DAG rechtfertigen den
  zusätzlichen Betriebsaufwand, sobald mehr als ein paar voneinander
  abhängige Jobs existieren.
- **Batch-COPY + Staging-Tabelle statt zeilenweisem INSERT**: der größte
  einzelne Hebel für den Durchsatz.
- **Reject-Tabelle statt Verwerfen fehlerhafter Zeilen**: SCADA-Sensoren
  fallen auf Arten aus, die wie echte Daten aussehen.
- **Wasserzeichen-basierte inkrementelle Extraktion statt Vollreload**.
- **Drei DAGs statt einem**: ein Ausfall bei NOAA oder Open-Meteo ist ein
  echter, externer, unvorhersehbarer Fehlerfall.
- **`pipeline_run_audit` teilen, aber nicht die Messwert-Tabellen**: Wind-
  und Solar-Audit-Zeilen haben identische Form; die Messwert-/Reject-/
  Wasserzeichen-Tabellen unterscheiden sich echt.
- **Eigenes Image pro Service statt eines gemeinsamen**: Airflows
  Basis-Image fixiert SQLAlchemy 1.4.x; Dashboard und dbt wollen aktuelle
  Versionen.
- **TimescaleDB statt manueller Partitionierung**.
- **Dashboard liest dbt-Marts statt dieselbe Aggregation doppelt zu
  implementieren**.
- **Slack-Alarmierung über einen einfachen `on_failure_callback` statt
  eines Airflow-Provider-Pakets**.

---

## 16. Roadmap / Erweiterungen <a name="16-roadmap--erweiterungen-de"></a>

- Den Simulator in `src/extract/scada_simulator.py` durch einen echten
  OPC-UA-/MQTT-Client oder einen Historian-Export ersetzen.
- `airflow dags test` in CI auf `external_data_sources` ausweiten, durch
  Mocken der Open-Meteo-/NOAA-HTTP-Aufrufe statt den DAG ganz zu
  überspringen.
- Den Slack-Alarmpfad an einen echten Workspace-Webhook anbinden und
  einen erzwungenen Task-Fehler bestätigen.
- `dbt source freshness` in CI validiert bisher nur die Konfiguration
  gegen eine leere Datenbank — die echte Prüfung müsste geplant gegen die
  Live-Pipeline-Daten laufen.
- GHCR-Images sind standardmäßig **privat**, auch bei einem öffentlichen
  Repository — die Sichtbarkeit muss einmalig manuell umgestellt werden.
- Zusätzliche NDBC-Stationen oder Open-Meteos Forecast-Endpunkt einbinden.
- `ambient_wind_daily_comparison` von einer Kalendertag-Granularität auf
  ein gleitendes Fenster umstellen.
- Einen dbt-Test (oder `dbt-expectations`) hinzufügen, der die
  Wind-/Wetter-/Bojen-Geschwindigkeiten auf plausible Abweichung prüft.
- Solars Klarhimmel-Modell nutzt feste UTC-Sonnenauf-/-untergangszeiten
  statt echter Sonnenstandsberechnung (z. B. via `pvlib`).
- Ein solares Äquivalent zu `ambient_wind_daily_comparison` hinzufügen.
