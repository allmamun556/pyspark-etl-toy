-- This is the payoff of integrating the two real external sources: a
-- direct daily comparison of the simulated turbine fleet's wind speed
-- against real ambient weather (Open-Meteo) and a real ocean buoy (NOAA
-- NDBC). A wind-farm operator would use something like this to sanity-check
-- whether SCADA anemometer readings are plausible against independent,
-- externally-sourced ground truth.
with fleet as (
    select reading_date, round(avg(avg_wind_speed_ms), 2) as fleet_avg_wind_speed_ms
    from {{ ref('turbine_daily_summary') }}
    group by 1
),

weather as (
    select reading_date, round(avg(wind_speed_ms), 2) as weather_avg_wind_speed_ms
    from {{ ref('stg_weather_api_readings') }}
    group by 1
),

buoy as (
    select reading_date, round(avg(wind_speed_ms), 2) as buoy_avg_wind_speed_ms
    from {{ ref('stg_iot_buoy_readings') }}
    group by 1
)

select
    coalesce(fleet.reading_date, weather.reading_date, buoy.reading_date) as reading_date,
    fleet.fleet_avg_wind_speed_ms,
    weather.weather_avg_wind_speed_ms,
    buoy.buoy_avg_wind_speed_ms
from fleet
full outer join weather using (reading_date)
full outer join buoy using (reading_date)
order by 1
