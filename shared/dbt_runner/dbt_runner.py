import logging

from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.results import RunExecutionResult


class PipelineException(Exception):
    pass


import logging
from collections import defaultdict
from typing import List, Tuple

from dbt.contracts.results import RunExecutionResult
from tabulate import tabulate


def _group_tables_by_prefix(results: RunExecutionResult) -> defaultdict:
    """
    Creates groups of tables based on their prefix. Available prefixes are 'stg_' for 'Staging',
    'int_' for 'Intermediate', or 'Marts' for others. Each table contains the  table name, status, and message
    """
    grouped_tables = defaultdict(list)

    for result in results:
        table_name = result.node.name
        status = result.status
        message = result.message

        prefix = "Staging" if table_name.startswith("stg_") else (
            "Intermediate" if table_name.startswith("int_") else "Marts")
        grouped_tables[prefix].append({"Table": table_name, "Status": status, "Message": message})

    return grouped_tables


def _generate_ascii_table_for_dbt_run_results(grouped_tables: defaultdict) -> Tuple[List, List]:
    """
        Generates an ASCII table representation from grouped tables. The table headers are 'Table', 'Status',
        and 'Message / Error Code'. Each group has its own row.
    """
    table_headers = ["Table", "Status", "Message / Error Code"]
    table_output = []

    for group, tables in grouped_tables.items():
        table_output.extend([[group, ""]] + [[table["Table"], table["Status"], table["Message"]] for table in tables])

    return table_headers, table_output


def _format_dbt_test_results_to_table(results: RunExecutionResult) -> Tuple[List, List]:
    """
    Takes result set of a dbt tests run, parses it and prepares a 2D array
    for tabulating. Each output row contains test name and its status.
    """
    table_headers = ["Test Name", "Status"]
    table_output = []

    for result in results:
        test_name = result.node.name
        status = result.status
        table_output.append([test_name, status])

    return table_headers, table_output


def generate_table_for_dbt_run_logging(results: RunExecutionResult) -> str:
    """
    Generates a table for logging purposes from the provided dbt run results.
    The table is grouped by prefix and formatted using ASCII art.
    """
    grouped_tables = _group_tables_by_prefix(results)
    table_headers, table_output = _generate_ascii_table_for_dbt_run_results(grouped_tables)

    return tabulate(table_output, headers=table_headers, tablefmt="grid")


def generate_table_for_dbt_test_logging(results: RunExecutionResult) -> str:
    """
    Takes results from a dbt test and generates an ASCII table.
    The table has two columns, 'Test Name' and 'Status', and each row represents a single test.
    """
    table_headers, table_output = _format_dbt_test_results_to_table(results)
    return tabulate(table_output, headers=table_headers, tablefmt="grid")


def log_dbt_results(results: RunExecutionResult, dbt_command: str, logger: logging.Logger) -> None:
    table_text = None
    if dbt_command == "run":
        table_text = generate_table_for_dbt_run_logging(results)
    elif dbt_command == "test":
        table_text = generate_table_for_dbt_test_logging(results)
    logger.info(table_text)


class DbtRunner:
    def __init__(self, dbt_dir):
        self.dbt_dir = dbt_dir

    @staticmethod
    def install_dbt_dependencies(dbt_dir: str) -> None:
        dbt = dbtRunner()
        # create CLI args as a list of strings
        cli_args = ["deps",
                    "--profiles-dir", dbt_dir,
                    "--project-dir", dbt_dir]
        res: dbtRunnerResult = dbt.invoke(cli_args)

        if res.exception:
            raise Exception(res.exception)

    def run_dbt(self, select_definition: str, logger: logging.Logger) -> None:
        """
        Executes a dbt run command with given select flag and environment.
        """
        dbt = dbtRunner()
        # create CLI args as a list of strings
        cli_args = ["run",
                    "-t", "prod",
                    "--select", select_definition]

        # run the command
        res: dbtRunnerResult = dbt.invoke(cli_args)

        if res.exception:
            raise Exception(res.exception)

        log_dbt_results(res.result, "run", logger)

        # if any error occurred, raise exception
        if self._status_in_results(res.result, "error"):
            raise PipelineException(
                "At least 1 error occurred in the execution of dbt run, check logged table for more "
                "information on which table/view failed to build")

    def test_dbt(self, select_definition: str, logger: logging.Logger) -> None:
        """
        Executes a dbt test command with given select flag and environment.
        """
        dbt = dbtRunner()
        # create CLI args as a list of strings
        cli_args = ["test",
                    "-t", "prod",
                    "--select", select_definition]

        # run the command
        res: dbtRunnerResult = dbt.invoke(cli_args)

        if res.exception:
            raise Exception(res.exception)

        log_dbt_results(res.result, "test", logger)

        # if any error occurred, raise exception
        if self._status_in_results(res.result, "fail"):
            raise PipelineException(
                "At least 1 failed test occurred in the execution of dbt test, check logged table for "
                "more information on which test failed")

    @staticmethod
    def _status_in_results(results: RunExecutionResult, status: str) -> bool:
        for result in results:
            if result.status == status:
                return True
        return False
