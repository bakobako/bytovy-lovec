from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from postgres_client import init_db_client, PostgresClient
from prefect.blocks.system import String
from prefect.cache_policies import NO_CACHE
from email_bot import EmailBot
import time
from bezrealitky_scraper import BezRealitkyScraper
from reality_idnes_scraper import RealityIdnesScraper
from sreality_scraper import SrealityScraper


def init_email_bot():
    api_key = Secret.load("resend-api-token").get()
    email_bot = EmailBot(api_key)
    return email_bot


def get_trackers(db_client):
    trackers = db_client.execute_query_and_fetch_dicts("SELECT tracker_id, customer_id, tracker_name "
                                                       "FROM real_estate_trackers.trackers")
    return trackers


def get_ads_to_send(db_client, tracker_id):
    get_real_estate_ads_query = f"""SELECT DISTINCT listing_url 
FROM public.matched_real_estate_listings 
WHERE tracker_id = {tracker_id}
    AND listing_id NOT IN (
        SELECT listing_id 
        FROM real_estate_trackers.tracker_notifications
        WHERE tracker_id = {tracker_id}
    ) 
    AND listing_id NOT IN (
        SELECT listing_id 
        FROM real_estate_listings.raw_real_estate_listings 
        WHERE is_active = FALSE
    );
    """
    ad_urls = db_client.execute_query(get_real_estate_ads_query)
    return [ad[0] for ad in ad_urls]


def get_ad_details(db_client, ads):
    ads_with_titles = {}
    for ad in ads:
        listing_id = db_client.execute_query_and_fetch_dicts(f"select listing_id from "
                                                             f"real_estate_listings.raw_real_estate_listings "
                                                             f"where listing_url = '{ad}'")[0]["listing_id"]
        get_ad_query = (f"SELECT district, street, area_m2, listing_price, currency ,apartment_layout"
                        f" FROM real_estate_listings.analysed_real_estate_listings WHERE listing_id = '{listing_id}'")

        ad_details = db_client.execute_query_and_fetch_dicts(get_ad_query)[0]

        url_description = (f"{ad_details['district']} - {ad_details['street']} - "
                           f"{ad_details['apartment_layout']} - {ad_details['area_m2']}m2 - "
                           f"{ad_details['listing_price']:,}{ad_details['currency']}")

        ads_with_titles[ad] = url_description
    return ads_with_titles


@task(cache_policy=NO_CACHE)
def process_tracker(db_client: PostgresClient, tracker_dict, email_bot, logger):
    get_user_data_query = (f"SELECT first_name, email FROM sales.customers "
                           f"WHERE customer_id = '{tracker_dict['customer_id']}'")
    user_data = db_client.execute_query_and_fetch_dicts(get_user_data_query)[0]
    email = user_data['email']
    user_name = user_data['first_name']

    new_ads = get_ads_to_send(db_client, tracker_dict['tracker_id'])

    new_ads_with_titles = get_ad_details(db_client, new_ads)

    subject = f"Found {len(new_ads)} new ads"
    logger.info(f"Sending email to {email} with {len(new_ads)} new ads")
    try:
        if new_ads:
            email_bot.send_email(email, subject, user_name, new_ads, new_ads_with_titles)
            for ad in new_ads:
                listing_id = db_client.execute_query_and_fetch_dicts(f"select listing_id from "
                                                                     f"real_estate_listings.raw_real_estate_listings "
                                                                     f"where listing_url = '{ad}'")[0]["listing_id"]
                db_client.insert_row("real_estate_trackers", "tracker_notifications",
                                     {"notification_method": "email",
                                      "sent_at": "now()",
                                      "tracker_id": tracker_dict['tracker_id'],
                                      "listing_id": listing_id})
    except Exception as e:
        print(f"Failed to send email to {email}, error: {e}")


def verify_listing(db_client, scrapers, listing_url):
    for scraper_name, scraper in scrapers.items():
        if scraper_name in listing_url:
            try:
                is_active, cont = scraper.validate_link(listing_url)
                if not is_active:
                    db_client.execute_query(f"""UPDATE real_estate_listings.raw_real_estate_listings 
                    set is_active = FALSE where listing_url = '{listing_url}';""")
                return
            except Exception as e:
                print(f"Failed to verify listing {listing_url}")
                print(e)
    raise Exception(f"Failed to verify listing {listing_url} because no scraper was found for it")


def verify_active_listings(db_client, scrapers):
    # TODO CHECK IF select listing_id from real_estate_trackers.tracker_notifications is okay,
    #  because if it was sent to one customer and not to another then this will not verify it
    listings_to_send = db_client.execute_query("""SELECT distinct 
    listing_url from public.matched_real_estate_listings 
    where listing_id not in (SELECT listing_id 
        FROM real_estate_listings.raw_real_estate_listings 
        WHERE is_active = FALSE)
    and  listing_id not in ( select listing_id from real_estate_trackers.tracker_notifications);
    """)
    for i, listing in enumerate(listings_to_send):
        print(f"Verifying listing {i + 1}/{len(listings_to_send)}")
        verify_listing(db_client, scrapers, listing[0])


def setup_scrapers(logger):
    br_scraper = BezRealitkyScraper(
        visited_links=[],
        logger=logger,
        headless=True
    )
    br_scraper.set_up_for_validation()
    sr_scraper = SrealityScraper(
        visited_links=[],
        logger=logger,
        headless=True
    )
    sr_scraper.set_up_for_validation()
    rid_scraper = RealityIdnesScraper(
        visited_links=[],
        logger=logger,
        headless=True
    )
    rid_scraper.set_up_for_validation()
    scrapers = {
        "bezrealitky.cz": br_scraper,
        "sreality.cz": sr_scraper,
        "reality.idnes.cz": rid_scraper
    }
    return scrapers


@flow
def notify_trackers_pipeline() -> None:
    db_client = init_db_client()
    email_bot = init_email_bot()
    logger = get_run_logger()
    trackers = get_trackers(db_client)
    scrapers = setup_scrapers(logger)
    verify_active_listings(db_client, scrapers)
    for tracker_dict in trackers:
        process_tracker(db_client, tracker_dict, email_bot, logger)


if __name__ == "__main__":
    notify_trackers_pipeline()
