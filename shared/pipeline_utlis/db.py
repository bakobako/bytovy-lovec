from shared.postgres_client.postgres_client import PostgresClient
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
