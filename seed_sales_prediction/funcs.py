from collections import namedtuple
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from seed_sales_prediction.backend.database_schema import ModelParameters
from seed_sales_prediction.backend.db_interface import get_session
from seed_sales_prediction.settings import EXPECTED_MONTHLY_SALES_VARIANCE


def process_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        (df.direction == 'OUTBOUND') & (df.orderId is not None) &
        (df.orderId != "") & (df.orderSecretKey is not None) &
        (df.orderSecretKey != "")]

    df = df[['quantity', 'createdAt']]
    df['date'] = pd.to_datetime(df.createdAt, unit='ms')
    df.drop('createdAt', axis=1, inplace=True)
    df.set_index('date', inplace=True)

    return df


SeedInfo = namedtuple('SeedInfo', ['seed_id', 'mean', 'standard_deviation'])


def create_prior_parameters(seed_id: str) -> SeedInfo:
    """Non-informative prior"""
    prior_mean = 150
    prior_std = 75
    return SeedInfo(seed_id=seed_id, mean=prior_mean, standard_deviation=prior_std)


def get_prior_parameters(seed_id: str) -> SeedInfo:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(seed_id)
        if not seed_item:
            return create_prior_parameters(seed_id)
        return SeedInfo(seed_item.seed_id, seed_item.mean, seed_item.standard_deviation)


def upload_updated_parameters(model_parameters: SeedInfo, latest_date: datetime) -> None:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(model_parameters.seed_id)
        # item does not yet exist
        if not seed_item:
            seed_item = ModelParameters(seed_id=model_parameters.seed_id, mean=model_parameters.mean,
                                        standard_deviation=model_parameters.standard_deviation, latest_date=latest_date)
            sess.add(seed_item)
        else:
            seed_item.mean = model_parameters.mean
            seed_item.standard_deviation = model_parameters.standard_deviation
            seed_item.latest_date = latest_date


def get_updated_parameters(prior_model_params: SeedInfo, new_data: pd.DataFrame) -> SeedInfo:
    prior_mu = prior_model_params.mean
    prior_var = prior_model_params.standard_deviation ** 2

    monthly_data = new_data.groupby(pd.Grouper(freq='M')).aggregate(
        ['sum', 'len', 'var'])['quantity']  # type: pd.DataFrame
    sum_x = monthly_data['sum'].sum()
    n_samples = monthly_data.shape[0]

    posterior_var = 1 / (1 / prior_var + n_samples / EXPECTED_MONTHLY_SALES_VARIANCE)
    posterior_mu = (1 / (1 / prior_var + n_samples / EXPECTED_MONTHLY_SALES_VARIANCE)) * \
                   (prior_mu / prior_var + sum_x / EXPECTED_MONTHLY_SALES_VARIANCE)

    return SeedInfo(seed_id=prior_model_params.seed_id, mean=posterior_mu, standard_deviation=np.sqrt(posterior_var))


def get_last_date_of_update(seed_id: str) -> Optional[datetime]:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(seed_id)
        if not seed_item:
            return None

        return seed_item.latest_date
