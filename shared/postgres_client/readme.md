# **PostgresClient**

A simple Python client for interacting with a PostgreSQL database, including executing queries, inserting rows, and retrieving data as dictionaries.

## **Features**

- Establishes a connection to a PostgreSQL database.
- Executes SQL queries with optional parameters.
- Inserts rows into a specified schema and table using dictionaries.
- Fetches table data as a list of dictionaries.

## **Usage**

```python
from postgres_client import PostgresClient  # Adjust the import path as needed

# Initialize the client
client = PostgresClient(
    host="db-bytovy-lovec.c962a8y428jz.eu-north-1.rds.amazonaws.com",
    port=5432,
    database="your_database_name",
    user="your_username",
    password="your_password"
)

# Insert a row
data = {"column1": "value1", "column2": 123}
client.insert_row(schema="public", table="your_table_name", data=data)

# Fetch data
rows = client.get_data(schema="public", table="your_table_name")
print(rows)
```