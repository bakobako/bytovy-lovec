with pipeline_runs as (
    select * from {{ source('cloud_infrastructure', 'pipeline_runs') }}
),

final as (
    select * from pipeline_runs
)

select * from final

