from datetime import datetime, timedelta
import pandas as pd
from prefect import get_client
from prefect.client.schemas.filters import FlowRunFilter, FlowFilter


async def download_recent_flow_runs(flow_name):
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)

    async with get_client() as client:
        # Step 1: Get the Flow ID using the flow name
        flows = await client.read_flows(flow_filter=FlowFilter(name={'eq_': flow_name}))
        if not flows:
            print(f"No flow found with name: {flow_name}")
            return None
        flow_id = flows[0].id  # Assuming the first match is correct

        # Step 2: Use Flow ID to filter Flow Runs
        flow_run_filter = FlowRunFilter(
            flow_id={'eq_': flow_id},
            start_time={'gte_': yesterday.isoformat()}
        )
        flow_runs = await client.read_flow_runs(flow_run_filter=flow_run_filter)
        fs = []
        for flow_run in flow_runs:
            if flow_run.flow_id == flow_id:
                fs.append(flow_run)

        if not fs:
            print(f"No flow runs found for '{flow_name}' in the past 24 hours")
            return None

        # Convert flow run data to DataFrame
        runs_data = [run.model_dump() for run in fs]
        df = pd.DataFrame(runs_data)

        # Save to CSV
        filename = f"{flow_name}_runs_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Downloaded {len(fs)} flow runs to {filename}")
        return df


# Example usage
if __name__ == "__main__":
    import asyncio

    FLOW_NAME = "run-real-estate-dbt"
    df = asyncio.run(download_recent_flow_runs(FLOW_NAME))
    print(df)
