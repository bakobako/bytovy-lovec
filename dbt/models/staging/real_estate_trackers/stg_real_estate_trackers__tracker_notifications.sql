with tracker_notifications as (
    select * from {{ source('real_estate_trackers', 'tracker_notifications') }}
),

final as (
    select * from tracker_notifications
)

select * from final

