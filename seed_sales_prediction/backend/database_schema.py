from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, TIMESTAMP


Base = declarative_base()


class ModelParameters(Base):
    """Store parameters for each seed id used for the predictive model."""
    __tablename__ = 'model_parameters'

    seed_id = Column(String(256), primary_key=True, nullable=False, comment="The seed id/name unique to each seed")

    mean = Column(Float, nullable=False, comment="The mean value in the normal distribution")
    standard_deviation = Column(Float, nullable=False, comment="The standard deviation in the normal distribution")
    latest_date = Column(TIMESTAMP(), nullable=True, comment='Timestamp with latest date of data used for update.')
