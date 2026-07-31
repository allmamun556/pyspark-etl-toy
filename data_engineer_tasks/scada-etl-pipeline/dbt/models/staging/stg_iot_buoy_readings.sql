select
    id,
    station_id,
    ts,
    ts::date as reading_date,
    wind_speed_ms,
    wind_gust_ms,
    wave_height_m,
    air_temp_c,
    water_temp_c,
    pressure_hpa,
    ingested_at
from {{ source('scada', 'iot_buoy_readings') }}
