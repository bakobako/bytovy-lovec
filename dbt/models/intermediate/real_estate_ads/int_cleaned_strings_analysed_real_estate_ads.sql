with analysed_real_estate_listings as (
    select * from {{ ref('stg_real_estate_listings__analysed_real_estate_listings') }}
),

raw_real_estate_listings as (
    select * from {{ ref('stg_real_estate_listings__raw_real_estate_listings') }}
),

joined_ad_data as (
    select
        raw_ad.listing_id,
        raw_ad.source_portal,
        raw_ad.listing_url,
        raw_ad.is_active,
        raw_ad.ingested_at,
        analysed_ad.property_type,
        analysed_ad.listing_price,
        analysed_ad.currency,
        analysed_ad.city,
        analysed_ad.district,
        analysed_ad.street,
        analysed_ad.house_number,
        analysed_ad.latitude,
        analysed_ad.longitude,
        analysed_ad.num_bedrooms,
        analysed_ad.num_bathrooms,
        analysed_ad.area_m2,
        analysed_ad.apartment_layout,
        analysed_ad.is_walkthrough_apartment,
        analysed_ad.floor_number,
        analysed_ad.building_floors,
        analysed_ad.type_of_ownership,
        analysed_ad.type_of_building,
        analysed_ad.condition,
        analysed_ad.energy_efficiency_label,
        analysed_ad.energy_usage,
        analysed_ad.monthly_payments_czk,
        analysed_ad.is_rooftop_apartment,
        analysed_ad.is_mezonet,
        analysed_ad.has_balcony,
        analysed_ad.balcony_area_m2,
        analysed_ad.has_terrace,
        analysed_ad.terrace_area_m2,
        analysed_ad.has_parking_spot,
        analysed_ad.has_garage,
        analysed_ad.has_elevator,
        analysed_ad.has_cellar,
        analysed_ad.cellar_area_m2,
        analysed_ad.flooring_type
    from raw_real_estate_listings raw_ad
    left join analysed_real_estate_listings analysed_ad
    on raw_ad.listing_id = analysed_ad.listing_id
),

cleaned_strings_analysed_real_estate_ads as (
    select
        listing_id,
        listing_url,
        lower(unaccent(trim(source_portal))) as source_portal,
        is_active,
        ingested_at,
        lower(unaccent(trim(property_type))) as property_type,
        listing_price,
        lower(unaccent(trim(currency))) as currency,
        lower(unaccent(trim(city))) as city,
        lower(unaccent(trim(district))) as district,
        lower(unaccent(trim(street))) as street,
        lower(unaccent(trim(house_number))) as house_number,
        latitude,
        longitude,
        num_bedrooms,
        num_bathrooms,
        area_m2,
        lower(unaccent(trim(apartment_layout))) as apartment_layout,
        is_walkthrough_apartment,
        floor_number,
        building_floors,
        lower(unaccent(trim(type_of_ownership))) as type_of_ownership,
        lower(unaccent(trim(type_of_building))) as type_of_building,
        lower(unaccent(trim(condition))) as condition,
        lower(unaccent(trim(energy_efficiency_label))) as energy_efficiency_label,
        lower(unaccent(trim(energy_usage))) as energy_usage,
        monthly_payments_czk,
        is_rooftop_apartment,
        is_mezonet,
        has_balcony,
        balcony_area_m2,
        has_terrace,
        terrace_area_m2,
        has_parking_spot,
        has_garage,
        has_elevator,
        has_cellar,
        cellar_area_m2,
        lower(unaccent(trim(flooring_type))) as flooring_type
    from joined_ad_data
    where is_active = true
)


select * from cleaned_strings_analysed_real_estate_ads
