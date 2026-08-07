-- Daily per-plant rollup, same shape as turbine_daily_summary.
select
    plant_id,
    reading_date,
    count(*) as reading_count,
    round(avg(irradiance_w_m2), 2) as avg_irradiance_w_m2,
    round(avg(dc_power_kw), 2) as avg_dc_power_kw,
    round(avg(ac_power_kw), 2) as avg_ac_power_kw,
    round(max(ac_power_kw), 2) as max_ac_power_kw,
    sum(case when is_anomalous then 1 else 0 end) as anomaly_count,
    round(
        100.0 * sum(case when status_code = 'operational' then 1 else 0 end) / count(*), 1
    ) as pct_operational,
    -- Capacity factor against DC nameplate (kWp), the standard PV metric -
    -- lower than wind's by nature (day/night cycle), which is expected,
    -- not a data quality issue.
    round(100.0 * avg(dc_power_kw) / {{ var('solar_capacity_kwp') }}, 2) as capacity_factor_pct
from {{ ref('stg_solar_readings') }}
group by 1, 2
