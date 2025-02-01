with int_deduplicated_analysed_real_estate_ads as (
    select * from {{ ref('int_deduplicated_analysed_real_estate_ads') }}
),

int_cleaned_strings_real_estate_trackers as (
    select * from {{ ref('int_cleaned_strings_real_estate_trackers') }}
),

matched_listings as (
    select
        ad.ad_url,
        tracker.account_id,
        tracker.listing_tracker_id,
        ad.ingested_timestamp
    from int_deduplicated_analysed_real_estate_ads ad
    inner join int_cleaned_strings_real_estate_trackers tracker
        ON ad.area_m2 between tracker.area_m2_from and tracker.area_m2_to
        AND ad.floor_number between tracker.floor_from and tracker.floor_to
        AND ad.price_czk between tracker.price_from and tracker.price_to
        AND ad.street = any(tracker.streets)
)

select * from matched_listings
