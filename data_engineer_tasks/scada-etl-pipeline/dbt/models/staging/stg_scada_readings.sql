-- Thin pass-through over the curated source table. Kept as its own model
-- (rather than having marts select from the source directly) so every
-- downstream model refs one place if a rename/cast is ever needed here.
select
    id,
    turbine_id,
    ts,
    ts::date as reading_date,
    wind_speed_ms,
    power_kw,
    rotor_rpm,
    nacelle_temp_c,
    pitch_angle_deg,
    status_code,
    is_anomalous,
    ingested_at,
    turbine_id || '-' || ts as reading_key
from {{ source('scada', 'scada_readings') }}
