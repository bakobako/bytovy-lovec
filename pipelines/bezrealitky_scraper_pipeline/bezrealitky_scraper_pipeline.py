from bezrealitky_scraper import BezRealitkyScraper
from postgres_client import init_db_client
from prefect import flow, get_run_logger


def check_if_url_in_db(url: str) -> bool:
    db_client = init_db_client()
    result = db_client.execute_query_and_fetch_dicts(
        f"SELECT listing_url FROM real_estate_listings.raw_real_estate_listings WHERE listing_url = '{url}'")
    return len(result) > 0


@flow
def download_bezrealitky_data():
    db_client = init_db_client()

    visited_links = db_client.execute_query_and_fetch_dicts("SELECT listing_url "
                                                            "FROM real_estate_listings.raw_real_estate_listings "
                                                            "where source_portal='bezrealitky';")
    visited_links = [link["listing_url"] for link in visited_links]

    logger = get_run_logger()

    scraper = BezRealitkyScraper(
        visited_links=visited_links,
        logger=logger,
        headless=True
    )
    scraper.run()

    logger.info(f"Found {len(scraper.new_link_data)} new ads")
    logger.info(f"Inserting to DB")
    for ad in scraper.new_link_data:
        if not check_if_url_in_db(ad["listing_url"]):
            db_client.insert_row(schema="real_estate_listings", table="raw_real_estate_listings", data=ad)


if __name__ == "__main__":
    download_bezrealitky_data()
