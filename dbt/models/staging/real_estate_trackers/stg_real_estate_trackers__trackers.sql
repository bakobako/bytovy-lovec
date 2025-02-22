with trackers as (
    select * from {{ source('real_estate_trackers', 'trackers') }}
),

final as (
    select  tracker_id,
            customer_id,
            tracker_name,
            property_type,
            min_price,
            max_price,
            min_bedrooms,
            max_bedrooms,
            min_square_meters,
            max_square_meters,
            min_floor,
            max_floor,
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

    from trackers
)

select * from final

