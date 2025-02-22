from postgres_client import init_db_client
from prefect import flow, get_run_logger
from reality_idnes_scraper import RealityIdnesScraper


@flow
def download_reality_idnes_data():
    db_client = init_db_client()

    visited_links = db_client.execute_query_and_fetch_dicts("SELECT listing_url "
                                                            "FROM real_estate_listings.raw_real_estate_listings "
                                                            "where source_portal='reality_idnes';")
    visited_links = [link["listing_url"] for link in visited_links]

    logger = get_run_logger()

    logger.info(f"Starting reality_idnes scraper")

    scraper = RealityIdnesScraper(
        visited_links=visited_links,
        logger=logger,
        headless=True
    )
    scraper.run()

    logger.info(f"Found {len(scraper.new_link_data)} new ads")
    logger.info(f"Inserting to DB")
    for ad in scraper.new_link_data:
        db_client.insert_row(schema="real_estate_listings", table="raw_real_estate_listings", data=ad)


if __name__ == "__main__":
    download_reality_idnes_data()
