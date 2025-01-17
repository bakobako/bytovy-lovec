from {{scraper_class_python_file}} import {{scraper_class_name}}

from prefect import task, flow, get_run_logger
from postgres_client import init_db_client


@flow
def {{scraper_download_function_name}}():
    db_client = init_db_client()

    visited_links = db_client.execute_query_and_fetch_dicts("SELECT ad_url "
                                                            "FROM raw.raw_real_estate_ads "
                                                            "where source_name='{{website_name}}';")
    visited_links = [link["ad_url"] for link in visited_links]
    broken_links = db_client.execute_query_and_fetch_dicts("SELECT ad_url from raw.raw_invalid_urls;")
    broken_links = [link["ad_url"] for link in broken_links]

    logger = get_run_logger()

    scraper = {{scraper_class_name}}(
        visited_links=visited_links,
        broken_links=broken_links,
        headless=True,
        logger=logger
    )
    scraper.run()

    logger.info(f"Found {len(scraper.new_link_data)} new ads")
    logger.info(f"Inserting to DB")

    for ad in scraper.new_link_data:
        db_client.insert_row(schema="raw", table="raw_real_estate_ads", data=ad)
    for link in scraper.new_broken_links:
        db_client.insert_row(schema="raw", table="raw_invalid_urls", data={"ad_url": link})


if __name__ == "__main__":
    {{scraper_download_function_name}}()
