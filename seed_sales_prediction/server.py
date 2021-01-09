import json

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


@app.put('/upload_data/{seed_id}/{json_url}')
def insert_tray(seed_id: str = Path(..., description="The id/name of the seed."),
                json_url: str = Path(..., description="The json url to get the data.")):

    df = get_dataset(json_url)
    df = process_dataset(df)
