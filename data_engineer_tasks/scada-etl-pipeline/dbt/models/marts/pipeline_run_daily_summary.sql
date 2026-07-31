-- Daily rollup of pipeline health, sourced from the same audit table the
-- dashboard's "Recent pipeline runs" panel reads - this is the trend view
-- (is reliability/throughput drifting?) that a single run can't show.
select
    run_date,
    count(*) as run_count,
    sum(case when status = 'success' then 1 else 0 end) as successful_runs,
    round(
        100.0 * sum(case when status = 'success' then 1 else 0 end) / count(*), 1
    ) as success_rate_pct,
    sum(rows_extracted) as total_rows_extracted,
    sum(rows_loaded) as total_rows_loaded,
    sum(rows_rejected) as total_rows_rejected,
    round(avg(duration_seconds), 2) as avg_duration_seconds,
    round(max(duration_seconds), 2) as max_duration_seconds
from {{ ref('stg_pipeline_run_audit') }}
group by 1
