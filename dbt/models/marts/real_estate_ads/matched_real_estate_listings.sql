with int_matched_listings as (
    select *
    from {{ ref('int_matched_listings') }}
),

final as (
    select *
    from int_matched_listings
)

select * from final
