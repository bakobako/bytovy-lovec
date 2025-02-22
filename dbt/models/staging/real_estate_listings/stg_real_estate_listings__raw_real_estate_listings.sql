with raw_real_estate_listings as (
    select * from {{ source('real_estate_listings', 'raw_real_estate_listings') }}
),

final as (
    select * from raw_real_estate_listings
)

select * from final

