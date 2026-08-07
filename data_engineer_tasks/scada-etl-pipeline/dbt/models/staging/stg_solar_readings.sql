select
    id,
    plant_id,
    ts,
    ts::date as reading_date,
    irradiance_w_m2,
    panel_temp_c,
    dc_power_kw,
    ac_power_kw,
    inverter_efficiency_pct,
    status_code,
    is_anomalous,
    ingested_at,
    plant_id || '-' || ts as reading_key
from {{ source('scada', 'solar_readings') }}
