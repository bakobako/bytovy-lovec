import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any
from prefect.blocks.system import Secret
from prefect.blocks.system import String


def init_db_client():
    db_name = String.load("db-bytovy-lovec-url").value
    password = Secret.load("db-bytovy-lovec-password").get()
    db_client = PostgresClient(host=db_name,
                               port=5432,
                               database="postgres",
                               user="bako",
                               password=password)
    return db_client


class PostgresClient:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Initialize the PostgresClient with connection parameters.

        :param host: The host of the PostgreSQL database.
        :param port: The port of the PostgreSQL database.
        :param database: The name of the PostgreSQL database.
        :param user: The username to authenticate with.
        :param password: The password to authenticate with.
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._connection = None

    def _create_connection(self) -> None:
        """
        Establish a connection to the PostgreSQL database.
        """
        self._connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        Execute a query with optional parameters and return the result.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the SQL query.
        :return: The result of the query if applicable.
        """
        try:
            if self._connection is None:
                self._create_connection()
            with self._connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                self._connection.commit()
        except psycopg2.Error as e:
            raise Exception(f"An error occurred: {e}")

    def insert_row(self, schema: str, table: str, data: Dict[str, Any]) -> None:
        """
        Insert a row into a specific table in a schema.

        If a conflict occurs (e.g., a unique constraint violation), no data is inserted.

        :param schema: The schema where the table resides.
        :param table: The table to insert data into.
        :param data: A dictionary of column names and their values.
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(f"%({k})s" for k in data.keys())
        query = (
            f"INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders}) "
            f"ON CONFLICT DO NOTHING"
        )

        try:
            self.execute_query(query, data)
        except psycopg2.Error as e:
            if self._connection:
                self._connection.rollback()  # Rollback transaction if it fails
            raise Exception(f"An error occurred during insert: {e}")

    def get_data(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """
        Retrieve data from a specific table in a schema as a list of dictionaries.

        :param schema: The schema where the table resides.
        :param table: The table to retrieve data from.
        :return: A list of dictionaries containing the table data.
        """
        query = f"SELECT * FROM {schema}.{table}"
        try:
            if self._connection is None:
                self._create_connection()
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"An error occurred while fetching data: {e}")

    def execute_query_and_fetch_dicts(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a query and return the result as a list of dictionaries.

        :param query: The query to execute.
        :return: A list of dictionaries containing the table data.
        """
        try:
            if self._connection is None:
                self._create_connection()
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"An error occurred while fetching data: {e}")
