from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the Base class that all models will inherit from
Base = declarative_base()

# Session maker for interacting with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)


# Function to create the engine based on the database URL
def get_engine(database_url: str):
    return create_engine(database_url)
