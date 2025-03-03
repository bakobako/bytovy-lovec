from prefect import flow, task, get_run_logger
from prefect.blocks.system import Secret
from slack_sdk import WebClient
from typing import List
from prefect.client.orchestration import get_client
from prefect.client.schemas import FlowRun
from prefect.client.schemas.filters import FlowRunFilter, FlowFilter
from postgres_client import PostgresClient, init_db_client
import asyncio
from datetime import datetime, timedelta, timezone
from prefect.cache_policies import NO_CACHE

PIPELINES_SLACK_CHANNEL = 'C08GDR4M7UY'
FLOW_LINK = ("https://app.prefect.cloud/account/5b5f662d-4a1d-408c-851d-4d0d8190d089/workspace/"
             "9c728a3e-9918-40bc-9dab-4febad37a646/flow-runs/flow-run/")


def send_message_to_slack(message: str) -> None:
    slack_token = Secret.load("slack-api-token").get()
    client = WebClient(token=slack_token)
    client.chat_postMessage(channel=PIPELINES_SLACK_CHANNEL, text=message)


async def _get_flow_runs(flow_names: List[str]) -> List[FlowRun]:
    async with get_client() as client:
        flow_filter = FlowFilter(name={"any_": flow_names})
        runs = await client.read_flow_runs(flow_run_filter=FlowRunFilter(flows=flow_filter))
        return runs


def get_flow_runs(flow_names: List[str]) -> List[FlowRun]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_get_flow_runs(flow_names))
    loop.close()
    return result


def get_failed_flows(flows: List[FlowRun], check_hours_ago: int) -> List[FlowRun]:
    filtered_flows = []
    check_time = datetime.now(timezone.utc) - timedelta(hours=check_hours_ago)
    for flow_data in flows:
        if flow_data.end_time:
            if flow_data.end_time >= check_time and flow_data.state.name.lower() in ["failed", "crashed", "timedout"]:
                filtered_flows.append(flow_data)
    return filtered_flows


def create_message(flows: List[FlowRun], flow_name: str) -> str:
    links = [{'url': f'{FLOW_LINK}{flow_data.id}', 'text': f'{flow_data.name}'}
             for flow_data in flows]
    message = "Hi, Team. Some of your pipelines have failed: \n" + "\n".join(
        [f"• {flow_name} - <{link['url']}|{link['text']}>" for link in links]
    )
    if len(flows) == 0:
        message = ""
    return message


def send_notifications_about_failed_flows(flows: List, flow_name: str, check_hours_ago: int):
    filtered_flows = get_failed_flows(flows, check_hours_ago)
    message = create_message(filtered_flows, flow_name)
    if len(message) > 0:
        send_message_to_slack(message)


def upload_flow_runs_to_db(db_client: PostgresClient, prefect_flows: List, flow_name: str) -> None:
    for prefect_flow in prefect_flows:
        if prefect_flow.end_time and prefect_flow.start_time:
            flow_data = {
                "run_id": str(prefect_flow.id),
                "pipeline_name": flow_name,
                "status": prefect_flow.state_name,
                "start_timestamp": prefect_flow.start_time,
                "end_timestamp": prefect_flow.end_time
            }
            db_client.insert_row(schema="cloud_infrastructure", table="pipeline_runs", data=flow_data)


@task(cache_policy=NO_CACHE)
def process_flow_by_name(flow_name: str, check_hours_ago: int, db_client: PostgresClient):
    logger = get_run_logger()
    prefect_flows = get_flow_runs([flow_name])
    logger.info(f"Found {len(prefect_flows)} flows with name {flow_name}")
    send_notifications_about_failed_flows(prefect_flows, flow_name, check_hours_ago)
    upload_flow_runs_to_db(db_client, prefect_flows, flow_name)


@flow
def pipeline_monitoring(flow_names: List[str], check_hours_ago: int = 24) -> None:
    db_client = init_db_client()
    for flow_name in flow_names:
        process_flow_by_name(flow_name, check_hours_ago, db_client)


if __name__ == "__main__":
    pipeline_monitoring(check_hours_ago=24,
                        flow_names=["download-bezrealitky-data",
                                    "download-reality-idnes-data",
                                    "download-srealty-data",
                                    "download-mm-reality-data",
                                    "download-s-williams-data",
                                    "notify-trackers",
                                    "process-raw-ads",
                                    "run-real-estate-dbt",
                                    "daily-summary"])
