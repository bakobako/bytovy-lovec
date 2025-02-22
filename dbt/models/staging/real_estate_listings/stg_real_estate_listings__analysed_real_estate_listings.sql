with analysed_real_estate_listings as (
    select * from {{ source('real_estate_listings', 'analysed_real_estate_listings') }}
),

final as (
    select * from analysed_real_estate_listings
)

select * from final

