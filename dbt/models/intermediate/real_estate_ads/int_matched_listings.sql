with int_deduplicated_analysed_real_estate_ads as (
    select * from {{ ref('int_deduplicated_analysed_real_estate_ads') }}
),

int_cleaned_strings_real_estate_trackers as (
    select * from {{ ref('int_cleaned_strings_real_estate_trackers') }}
),

matched_listings as (
    select
        ad.listing_id as listing_id,
        ad.listing_url as listing_url,
        tracker.customer_id as customer_id,
        tracker.tracker_id as tracker_id
    from int_deduplicated_analysed_real_estate_ads ad
    inner join int_cleaned_strings_real_estate_trackers tracker
        ON ad.area_m2 between tracker.min_square_meters and tracker.max_square_meters
        AND ad.floor_number between tracker.min_floor and tracker.max_floor
        AND ad.listing_price between tracker.min_price and tracker.max_price
        AND ad.street = any(tracker.streets)
)

select * from matched_listings
