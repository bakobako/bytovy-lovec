with raw_analysed_real_estate_ads as (
    select * from {{ ref('stg_raw__analysed_real_estate_ads') }}
),

cleaned_strings_analysed_real_estate_ads as (
    select
        ad_url,
        source_name,
        lower(unaccent(whole_address)) as whole_address,
        lower(unaccent(area)) as area,
        trim(lower(unaccent(street))) as street,
        area_m2,
        price_czk,
        price_per_m2_czk,
        apartment_layout,
        number_of_bedrooms,
        is_walkthrough_apartment,
        floor_number,
        building_floors,
        ownership,
        lower(unaccent(type_of_building)) as type_of_building,
        lower(unaccent(condition)) as condition,
        energy_efficiency_label,
        energy_usage,
        monthly_payments_czk,
        is_rooftop_apartment,
        mezonet,
        balcony,
        balcony_area_m2,
        terase,
        terase_area_m2,
        parking_spot,
        garage,
        elevator,
        cellar,
        cellar_area_m2,
        lower(unaccent(flooring_type)) as flooring_type,
        bathroom_layout,
        ingested_timestamp
    from raw_analysed_real_estate_ads
)

select * from cleaned_strings_analysed_real_estate_ads
