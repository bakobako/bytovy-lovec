with customers as (
    select * from {{ source('sales', 'customers') }}
),

final as (
    select * from customers
)

select * from final

