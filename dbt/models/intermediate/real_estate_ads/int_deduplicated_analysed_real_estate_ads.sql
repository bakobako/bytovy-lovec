with int_cleaned_strings_analysed_real_estate_ads as (
    select * from {{ ref('int_cleaned_strings_analysed_real_estate_ads') }}
),

deduplicated_analysed_real_estate_ads as (
    select
        distinct on (street, price_czk, apartment_layout, area_m2) *
    from int_cleaned_strings_analysed_real_estate_ads
    order by street, price_czk, apartment_layout, area_m2, ingested_timestamp desc
)

select * from deduplicated_analysed_real_estate_ads