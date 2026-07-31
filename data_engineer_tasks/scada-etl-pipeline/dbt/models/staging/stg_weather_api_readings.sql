select
    id,
    source,
    latitude,
    longitude,
    ts,
    ts::date as reading_date,
    wind_speed_ms,
    wind_direction_deg,
    temperature_c,
    pressure_hpa,
    ingested_at
from {{ source('scada', 'weather_api_readings') }}
