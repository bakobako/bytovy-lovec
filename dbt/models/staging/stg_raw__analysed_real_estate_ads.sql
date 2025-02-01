with analysed_real_estate_ads as (
    select * from {{ source('raw', 'analysed_real_estate_ads') }}
),

final as (
    select
        ad_url,
        source_name,
        whole_address,
        area,
        street,
        area_m2,
        price_czk,
        price_per_m2_czk,
        apartment_layout,
        number_of_bedrooms,
        is_walkthrough_apartment,
        floor_number,
        building_floors,
        ownership,
        type_of_building,
        condition,
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
        flooring_type,
        bathroom_layout,
        ingested_timestamp
    from analysed_real_estate_ads
)

select * from final

