select
    id,
    dag_run_id,
    task_id,
    started_at::date as run_date,
    rows_extracted,
    rows_loaded,
    rows_rejected,
    duration_seconds,
    status,
    started_at,
    finished_at
from {{ source('scada', 'pipeline_run_audit') }}
