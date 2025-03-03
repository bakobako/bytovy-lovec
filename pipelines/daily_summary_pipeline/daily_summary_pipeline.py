from prefect import flow
from prefect.blocks.system import Secret
from slack_sdk import WebClient
from postgres_client import PostgresClient, init_db_client
from datetime import datetime

PIPELINES_SLACK_CHANNEL = 'C08FHEL2HGE'


def send_message_to_slack(message: str) -> None:
    slack_token = Secret.load("slack-api-token").get()
    client = WebClient(token=slack_token)
    client.chat_postMessage(channel=PIPELINES_SLACK_CHANNEL, text=message)


def get_added_real_estate_listings(db_client: PostgresClient):
    query = """
    SELECT source_portal, COUNT(*) as listings_count
    FROM real_estate_listings.raw_real_estate_listings
    WHERE ingested_at >= NOW() - INTERVAL '24 HOURS'
    GROUP BY source_portal;
    """
    result = db_client.execute_query_and_fetch_dicts(query)
    clean_result = {}
    for r in result:
        portal = r["source_portal"]
        listings_count = r["listings_count"]
        clean_result[portal] = listings_count
    return clean_result


def get_number_of_trackers(db_client: PostgresClient):
    query = """
    SELECT COUNT(DISTINCT tracker_id) as tracker_count
    FROM real_estate_trackers.tracker_notifications
    WHERE sent_at >= NOW() - INTERVAL '24 HOURS';
    """
    result = db_client.execute_query_and_fetch_dicts(query)
    return result[0]["tracker_count"]


def get_sent_real_estate_listings(db_client: PostgresClient):
    query = """
    SELECT COUNT(*) as sent_listings_count
    FROM real_estate_trackers.tracker_notifications
    WHERE sent_at >= NOW() - INTERVAL '24 HOURS';
    """
    result = db_client.execute_query_and_fetch_dicts(query)
    return result[0]["sent_listings_count"]


@flow
def daily_summary() -> None:
    db_client = init_db_client()
    real_estate_listings_added = get_added_real_estate_listings(db_client)
    num_trackers = get_number_of_trackers(db_client)
    sent_real_estate_listings = get_sent_real_estate_listings(db_client)
    message = f"""Daily summary for {datetime.now().strftime('%Y-%m-%d')}:\n
{real_estate_listings_added}\n
Number of trackers notified today: {num_trackers}\n
Number of listings sent today: {sent_real_estate_listings}"""
    send_message_to_slack(message)


if __name__ == "__main__":
    daily_summary()
