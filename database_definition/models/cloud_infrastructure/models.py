from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP
from database_definition.models.base import Base

class PipelineRun(Base):
    __tablename__ = 'pipeline_runs'
    __table_args__ = {'schema': 'cloud_infrastructure'}

    run_id = Column(Integer, primary_key=True)
    pipeline_name = Column(String, nullable=False)
    start_timestamp = Column(TIMESTAMP, nullable=False)
    end_timestamp = Column(TIMESTAMP, nullable=False)
    status = Column(String, nullable=False)  # e.g., success, failed

