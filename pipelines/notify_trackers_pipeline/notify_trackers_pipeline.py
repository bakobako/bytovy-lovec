from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from postgres_client import init_db_client, PostgresClient
from prefect.blocks.system import String
from prefect.cache_policies import NO_CACHE
from email_bot import EmailBot


def init_email_bot():
    api_key = Secret.load("resend-api-token").get()
    email_bot = EmailBot(api_key)
    return email_bot


def get_trackers(db_client):
    trackers = db_client.execute_query_and_fetch_dicts("SELECT id, account_id FROM raw.listing_tracker")
    return trackers


def get_ads_to_send(db_client, tracker_id):
    get_matched_real_estate_ads_query = f"select ad_url from matched_real_estate_listings where listing_tracker_id = '{tracker_id}'"
    matched_ads = db_client.execute_query(get_matched_real_estate_ads_query)
    matched_ads = [matched_ad[0] for matched_ad in matched_ads]

    sent_ads_query = f"select ad_url from raw.sent_listings_of_trackers where listing_tracker_id = '{tracker_id}'"
    sent_ads = db_client.execute_query(sent_ads_query)
    sent_ads = [sent_ad[0] for sent_ad in sent_ads]

    new_ads = [ad for ad in matched_ads if ad not in sent_ads]
    return new_ads


def get_ad_details(db_client, ads):
    ads_with_titles = {}
    for ad in ads:
        get_ad_query = (f"SELECT whole_address, street, area_m2, price_czk, apartment_layout"
                        f" FROM raw.analysed_real_estate_ads WHERE ad_url = '{ad}'")

        ad_details = db_client.execute_query_and_fetch_dicts(get_ad_query)[0]

        url_description = (f"{ad_details['whole_address']} - {ad_details['street']} - "
                           f"{ad_details['apartment_layout']} - {ad_details['area_m2']}m2 - "
                           f"{ad_details['price_czk']:,}CZK")

        ads_with_titles[ad] = url_description
    return ads_with_titles


@task(cache_policy=NO_CACHE)
def process_tracker(db_client: PostgresClient, tracker_dict, email_bot):
    get_user_data_query = f"SELECT email, first_name FROM raw.account WHERE account_id = '{tracker_dict['account_id']}'"
    user_data = db_client.execute_query_and_fetch_dicts(get_user_data_query)[0]
    email = user_data['email']
    user_name = user_data['first_name']

    new_ads = get_ads_to_send(db_client, tracker_dict['id'])

    new_ads_with_titles = get_ad_details(db_client, new_ads)

    subject = f"Found {len(new_ads)} new ads"

    try:
        if new_ads:
            email_bot.send_email(email, subject, user_name, new_ads, new_ads_with_titles)
            for ad in new_ads:
                db_client.insert_row("raw", "sent_listings_of_trackers",
                                     {"listing_tracker_id": tracker_dict['id'], "ad_url": ad})
    except Exception as e:
        print(f"Failed to send email to {email}, error: {e}")


@flow
def notify_trackers_pipeline() -> None:
    db_client = init_db_client()
    email_bot = init_email_bot()

    trackers = get_trackers(db_client)
    for tracker_dict in trackers:
        process_tracker(db_client, tracker_dict, email_bot)


if __name__ == "__main__":
    notify_trackers_pipeline()
