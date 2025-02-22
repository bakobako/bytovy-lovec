with listing_trackers as (
    select * from {{ ref('stg_real_estate_trackers__trackers') }}
),

cleaned_strings_real_estate_trackers as (
    select
        tracker_id,
        customer_id,
        tracker_name,
        property_type,
        coalesce(min_square_meters, 0) as min_square_meters,
        coalesce(max_square_meters, 1000) as max_square_meters,
        coalesce(min_floor, 0) as min_floor,
        coalesce(max_floor, 100) as max_floor,
        coalesce(min_bedrooms, 0) as min_bedrooms,
        coalesce(max_bedrooms, 100) as max_bedrooms,
        coalesce(min_price, 0) as min_price,
        coalesce(max_price, 1000000000) as max_price,
        {{ lower_and_unaccent_array('disposition') }} as disposition,
        {{ lower_and_unaccent_array('streets') }} as streets,
        {{ lower_and_unaccent_array('ownership') }} as ownership,
        {{ lower_and_unaccent_array('building_type') }} as building_type,
        {{ lower_and_unaccent_array('condition') }} as condition,
        {{ lower_and_unaccent_array('energy_efficiency') }} as energy_efficiency,
        coalesce(required_balcony, false) as required_balcony,
        coalesce(required_terrace, false) as required_terrace,
        coalesce(required_garage, false) as required_garage,
        coalesce(required_parking_space, false) as required_parking_space,
        coalesce(required_elevator, false) as required_elevator
    from listing_trackers
)

select * from cleaned_strings_real_estate_trackers
