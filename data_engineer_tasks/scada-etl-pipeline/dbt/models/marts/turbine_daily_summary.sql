-- Daily per-turbine rollup: the kind of mart an availability/production
-- report or dashboard would query, instead of scanning raw readings.
select
    turbine_id,
    reading_date,
    count(*) as reading_count,
    round(avg(wind_speed_ms), 2) as avg_wind_speed_ms,
    round(avg(power_kw), 2) as avg_power_kw,
    round(max(power_kw), 2) as max_power_kw,
    round(min(power_kw), 2) as min_power_kw,
    sum(case when is_anomalous then 1 else 0 end) as anomaly_count,
    round(
        100.0 * sum(case when status_code = 'operational' then 1 else 0 end) / count(*), 1
    ) as pct_operational,
    -- Capacity factor: average output as a % of rated capacity. Standard
    -- wind-industry metric for how much of a turbine's nameplate potential
    -- was actually delivered over the period.
    round(100.0 * avg(power_kw) / {{ var('rated_power_kw') }}, 2) as capacity_factor_pct
from {{ ref('stg_scada_readings') }}
group by 1, 2
