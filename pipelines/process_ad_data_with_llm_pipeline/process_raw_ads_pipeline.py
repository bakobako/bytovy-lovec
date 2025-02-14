from ai_client import AIClient
from postgres_client import init_db_client
from prefect.blocks.system import Secret
from prefect import task, flow


@task
def fetch_raw_ads(db_client):
    processed_ads = db_client.execute_query_and_fetch_dicts("""SELECT * FROM raw.raw_real_estate_ads 
    WHERE ad_url NOT IN (
    SELECT ad_url FROM raw.analysed_real_estate_ads );""")
    return processed_ads


@flow
def process_raw_ads():
    db_client = init_db_client()
    ai_api_key = Secret.load("google-gemini-flash-api-key").get()
    ai_client = AIClient(api_key=ai_api_key)
    raw_ads = fetch_raw_ads(db_client)
    for raw_ad in raw_ads:
        ad_text = raw_ad["ad_text"]
        try:
            response = ai_client.analyse_real_estate_ad(ad_text)
            response["ad_url"] = raw_ad["ad_url"]
            response["source_name"] = raw_ad["source_name"]
            response['ingested_timestamp'] = raw_ad['ingested_timestamp']
            db_client.insert_row(schema="raw", table="analysed_real_estate_ads", data=response)
            print(f"Processed ad: {raw_ad['ad_url']}")
        except Exception as e:
            print(f"Failed to process ad: {raw_ad['ad_url']}, error: {e}")


if __name__ == "__main__":
    process_raw_ads()
