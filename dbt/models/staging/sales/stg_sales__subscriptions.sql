with subscriptions as (
    select * from {{ source('sales', 'subscriptions') }}
),

final as (
    select * from subscriptions
)

select * from final

