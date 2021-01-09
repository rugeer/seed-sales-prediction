import json
from collections import namedtuple

from seed_sales_prediction.backend.db_interface import get_session
from seed_sales_prediction.backend.database_schema import ModelParameters

from fastapi import FastAPI, Path
import pandas as pd
from urllib import request


app = FastAPI()


def get_dataset(url: str) -> pd.DataFrame:
    with request.urlopen(url) as url:
        data = json.loads(url.read().decode())

    return pd.DataFrame.from_dict(data)


def process_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        (df.direction == 'OUTBOUND') & (df.orderId is not None) &
        (df.orderId != "") & (df.orderSecretKey is not None) &
        (df.orderSecretKey != "")]

    df = df[['quantity', 'createdAt']]
    df['date'] = pd.to_datetime(df.createdAt, unit='ms')
    df.drop('createdAt', axis=1, inplace=True)
    df.set_index('date', inplace=True)
    df.index = df.index.date
    df.index.rename('date', inplace=True)

    return df


SeedInfo = namedtuple('SeedInfo', ['seed_id', 'mean', 'standard_deviation'])


def get_prior_parameters(seed_id: str) -> SeedInfo:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(seed_id)

        return SeedInfo(seed_item.seed_id, seed_item.mean, seed_item.standard_deviation)


def upload_updated_parameters(seed_id: str, mean: float, standard_deviation: float) -> None:
    with get_session() as sess:
        seed_item = sess.query(ModelParameters).get(seed_id)
        seed_item.mean = mean
        seed_item.standard_deviation = standard_deviation


ModelParams = namedtuple('ModelParams', ['mean', 'standard_deviation'])

def get_updated_parameters(prior_model_params: ModelParams, new_data) -> ModelParams:
    posterior_mu =
    posterior_std =


@app.put('/upload_data/{seed_id}/{json_url}')
def insert_tray(seed_id: str = Path(..., description="The id/name of the seed."),
                json_url: str = Path(..., description="The json url to get the data.")):

    df = get_dataset(json_url)
    df = process_dataset(df)
    current_params = get_prior_parameters(seed_id)

