with raw_listing_tracker as (
    select * from {{ ref('stg_raw__listing_tracker') }}
),

cleaned_strings_real_estate_trackers as (
    select
        listing_tracker_id,
        account_id,
        coalesce(area_m2_from, 0) as area_m2_from,
        coalesce(area_m2_to, 1000) as area_m2_to,
        coalesce(floor_from, 0) as floor_from,
        coalesce(floor_to, 100) as floor_to,
        coalesce(price_from, 0) as price_from,
        coalesce(price_to, 1000000000) as price_to,
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
    from raw_listing_tracker
)

select * from cleaned_strings_real_estate_trackers
