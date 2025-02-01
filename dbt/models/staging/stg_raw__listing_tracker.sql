with listing_tracker as (
    select * from {{ source('raw', 'listing_tracker') }}
),

final as (
    select
        id as listing_tracker_id,
        account_id,
        area_m2_from,
        area_m2_to,
        floor_from,
        floor_to,
        price_from,
        price_to,
        array(SELECT jsonb_array_elements(preferences->'disposition')) as disposition,
        array(SELECT jsonb_array_elements(preferences->'streets')) as streets,
        array(SELECT jsonb_array_elements(preferences->'ownership')) as ownership,
        array(SELECT jsonb_array_elements(preferences->'building_type')) as building_type,
        array(SELECT jsonb_array_elements(preferences->'condition')) as condition,
        array(SELECT jsonb_array_elements(preferences->'energy_efficiency')) as energy_efficiency,
        (preferences->'accessories'->>'balcony')::boolean as required_balcony,
        (preferences->'accessories'->>'terrace')::boolean as required_terrace,
        (preferences->'accessories'->>'garage')::boolean as required_garage,
        (preferences->'accessories'->>'parking_space')::boolean as required_parking_space,
        (preferences->'accessories'->>'elevator')::boolean as required_elevator
    from listing_tracker
)

select * from final
