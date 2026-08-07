-- Portfolio-level view across both simulated fleets: what a renewable
-- operator running mixed wind + solar assets would actually want on one
-- dashboard row, rather than two disconnected reports.
with wind as (
    select
        reading_date,
        count(distinct turbine_id) as turbine_count,
        sum(avg_power_kw) as wind_total_avg_power_kw
    from {{ ref('turbine_daily_summary') }}
    group by 1
),

solar as (
    select
        reading_date,
        count(distinct plant_id) as plant_count,
        sum(avg_dc_power_kw) as solar_total_avg_dc_power_kw
    from {{ ref('solar_daily_summary') }}
    group by 1
)

select
    coalesce(wind.reading_date, solar.reading_date) as reading_date,
    wind.turbine_count,
    round(wind.wind_total_avg_power_kw, 2) as wind_total_avg_power_kw,
    solar.plant_count,
    round(solar.solar_total_avg_dc_power_kw, 2) as solar_total_avg_dc_power_kw,
    round(
        coalesce(wind.wind_total_avg_power_kw, 0) + coalesce(solar.solar_total_avg_dc_power_kw, 0), 2
    ) as combined_total_avg_power_kw
from wind
full outer join solar using (reading_date)
order by 1
