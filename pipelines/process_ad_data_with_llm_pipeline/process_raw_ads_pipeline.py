from ai_client import AIClient
from postgres_client import init_db_client
from prefect.blocks.system import Secret
from prefect.cache_policies import NO_CACHE
from prefect import task, flow, get_run_logger


@task(cache_policy=NO_CACHE)
def fetch_raw_ads(db_client):
    processed_ads = db_client.execute_query_and_fetch_dicts("""SELECT * FROM 
    real_estate_listings.raw_real_estate_listings 
    WHERE listing_id NOT IN (
    SELECT listing_id FROM real_estate_listings.analysed_real_estate_listings );""")
    return processed_ads


@task(cache_policy=NO_CACHE)
def process_raw_ad(raw_ad, db_client, ai_client, logger):
    ad_text = raw_ad["ad_text"]
    listing_id = raw_ad["listing_id"]
    try:
        response = ai_client.analyse_real_estate_ad(ad_text)
        response["listing_id"] = listing_id
        if response["listing_price"] is None:
            response["listing_price"] = 0
        db_client.insert_row(schema="real_estate_listings", table="analysed_real_estate_listings", data=response)
        logger.info(f"Processed ad: {raw_ad['listing_url']}")
    except Exception as e:
        logger.error(f"Failed to process ad: {raw_ad['listing_url']}, error: {e}")
        raise e


@flow
def process_raw_ads():
    db_client = init_db_client()
    ai_api_key = Secret.load("google-gemini-flash-api-key").get()
    ai_client = AIClient(api_key=ai_api_key)
    raw_ads = fetch_raw_ads(db_client)
    logger = get_run_logger()
    for raw_ad in raw_ads:
        process_raw_ad(raw_ad, db_client, ai_client, logger)


if __name__ == "__main__":
    process_raw_ads()
