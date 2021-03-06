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
        (df.direction == "OUTBOUND")
        & (df.order_id is not None)
        & (df.order_id != "")
        & (df.order_secret_key is not None)
        & (df.order_secret_key != "")
    ]

    df = df[["quantity", "created_at"]]
    df["date"] = pd.to_datetime(df.created_at, unit="ms")
    df.drop("created_at", axis=1, inplace=True)
    df.set_index("date", inplace=True)

    return df


SeedInfo = namedtuple("SeedInfo", ["seed_id", "mean", "standard_deviation"])


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


def upload_updated_parameters(
    model_parameters: SeedInfo, latest_date: datetime
) -> None:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(model_parameters.seed_id)
        # item does not yet exist
        if not seed_item:
            seed_item = ModelParameters(
                seed_id=model_parameters.seed_id,
                mean=model_parameters.mean,
                standard_deviation=model_parameters.standard_deviation,
                latest_date=latest_date,
            )
            sess.add(seed_item)
        else:
            seed_item.mean = model_parameters.mean
            seed_item.standard_deviation = model_parameters.standard_deviation
            seed_item.latest_date = latest_date


def get_updated_parameters(
    prior_model_params: SeedInfo, new_data: pd.DataFrame
) -> SeedInfo:
    prior_mu = prior_model_params.mean
    prior_var = prior_model_params.standard_deviation ** 2

    monthly_data = new_data.groupby(pd.Grouper(freq="M")).sum()
    sum_x = monthly_data.sum().values[0]
    n_samples = monthly_data.shape[0]

    posterior_var = 1 / (1 / prior_var + n_samples / EXPECTED_MONTHLY_SALES_VARIANCE)
    posterior_mu = (
        1 / (1 / prior_var + n_samples / EXPECTED_MONTHLY_SALES_VARIANCE)
    ) * (prior_mu / prior_var + sum_x / EXPECTED_MONTHLY_SALES_VARIANCE)

    return SeedInfo(
        seed_id=prior_model_params.seed_id,
        mean=posterior_mu,
        standard_deviation=np.sqrt(posterior_var),
    )


def get_last_date_of_update(seed_id: str) -> Optional[datetime]:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(seed_id)
        if not seed_item:
            return None

        return seed_item.latest_date


Predictions = namedtuple(
    "Predictions", ["expected_value", "lower_bound_95", "upper_bound_95"]
)


def predict_one_year_sales(params: SeedInfo):
    mu_one_year = params.mean * 12
    var_one_year = (params.standard_deviation ** 2) * 12
    lower_bound = mu_one_year - 2 * np.sqrt(var_one_year)
    upper_bound = mu_one_year + 2 * np.sqrt(var_one_year)
    return Predictions(
        expected_value=round(mu_one_year, 1),
        lower_bound_95=round(lower_bound, 1),
        upper_bound_95=round(upper_bound, 1),
    )
