import os

from dbt_runner import DbtRunner
from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect.blocks.system import String


@task
def install_dbt_dependencies(dbt_runner: DbtRunner, dbt_dir: str):
    dbt_runner.install_dbt_dependencies(dbt_dir=dbt_dir)


@task
def run_dbt(dbt_runner: DbtRunner, select_definition: str, run_logger):
    dbt_runner.run_dbt(select_definition=select_definition, logger=run_logger)


@task
def run_test_dbt(dbt_runner: DbtRunner, select_definition: str, run_logger):
    dbt_runner.test_dbt(select_definition=select_definition, logger=run_logger)


def set_credentials() -> None:
    secret_block = Secret.load("db-bytovy-lovec-password")
    secret = secret_block.get()
    os.environ.update({"DBT_ENV_SECRET_PROD": secret})

    db_url = String.load("db-bytovy-lovec-url").value
    os.environ.update({"DBT_ENV_URL_PROD": db_url})


@flow
def run_cloud_dbt(dbt_dir: str = "../../dbt") -> None:
    """
    Sets up credentials and executes dbt run command for marts (and all their downstream models)
    in a specified environment.
    """
    set_credentials()

    dbt_runner = DbtRunner(dbt_dir)
    select_definition = "+marts.real_estate_ads"

    run_logger = get_run_logger()

    install_dbt_dependencies(dbt_runner, dbt_dir)

    run_dbt(dbt_runner, select_definition, run_logger)
    run_test_dbt(dbt_runner, select_definition, run_logger)


if __name__ == "__main__":
    run_cloud_dbt(dbt_dir="../../dbt")
