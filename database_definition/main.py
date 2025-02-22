import os
import sys
from sqlalchemy import create_engine, text
from database_definition.models.base import Base, get_engine
from models.sales.models import *
from models.real_estate_listings.models import *
from models.real_estate_trackers.models import *
from models.cloud_infrastructure.models import *


def create_schemas(engine):
    schemas = [obj for obj in os.listdir('database_definition/models') if not obj.endswith('.py')]
    with engine.connect() as connection:
        for schema in schemas:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            connection.commit()
            print(f"Schema '{schema}' created (if it didn't already exist).")


# Function to create all tables
def create_tables(engine):
    Base.metadata.create_all(bind=engine)
    print("All tables have been created successfully!")


def execute_sql_from_file(connection, file_path):
    with open(file_path, 'r') as file:
        sql = file.read()
        connection.execute(text(sql))
        connection.commit()


# Main function
def main(database_url):
    engine = get_engine(database_url)
    create_schemas(engine)
    create_tables(engine)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <DATABASE_URL>")
        sys.exit(1)

    # Get the database URL from the command line argument
    database_url = sys.argv[1]

    # Initialize the database
    main(database_url)
