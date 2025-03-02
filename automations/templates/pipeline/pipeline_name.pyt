from {{scraper_class_python_file}} import {{scraper_class_name}}

from prefect import task, flow, get_run_logger
from postgres_client import init_db_client

def check_if_url_in_db(url: str) -> bool:
    db_client = init_db_client()
    result = db_client.execute_query_and_fetch_dicts(
        f"SELECT listing_url FROM real_estate_listings.raw_real_estate_listings WHERE listing_url = '{url}'")
    return len(result) > 0

@flow
def {{scraper_download_function_name}}():
    db_client = init_db_client()

    visited_links = db_client.execute_query_and_fetch_dicts("SELECT ad_url "
                                                            "FROM raw.raw_real_estate_ads "
                                                            "where source_name='{{website_name}}';")
    visited_links = [link["ad_url"] for link in visited_links]

    logger = get_run_logger()

    scraper = {{scraper_class_name}}(
        visited_links=visited_links,
        headless=True,
        logger=logger
    )
    scraper.run()

    logger.info(f"Found {len(scraper.new_link_data)} new ads")
    logger.info(f"Inserting to DB")
    for ad in scraper.new_link_data:
        if not check_if_url_in_db(ad["listing_url"]):
            db_client.insert_row(schema="real_estate_listings", table="raw_real_estate_listings", data=ad)


if __name__ == "__main__":
    {{scraper_download_function_name}}()
