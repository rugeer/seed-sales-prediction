from typing import List, Optional
from datetime import time

from pydantic import BaseModel

from fastapi import FastAPI, Path, Body
import pandas as pd

from seed_sales_prediction.funcs import (get_prior_parameters, get_updated_parameters, process_dataset,
                                         upload_updated_parameters, get_last_date_of_update)

app = FastAPI()


class NewData(BaseModel):
    """API Schema for new data."""
    direction: str
    order_id: Optional[str]
    order_secret_key: Optional[str]
    quantity: int
    created_at: time




@app.put('/upload_data/{seed_id}')
def insert_tray(seed_id: str = Path(..., description="The id/name of the seed."),
                new_data: List[NewData] = Body(
                    ..., description="The json url to get the data. Data should be complete per each month, i.e., "
                                     "should not upload half-month data only")):
    latest_date = get_last_date_of_update(seed_id)
    df = pd.DataFrame(new_data)
    df = process_dataset(df)
    # only consider new data
    if latest_date:
        df = df[df.index > latest_date]  # TODO: check logic correct

    current_params = get_prior_parameters(seed_id)
    posterior_params = get_updated_parameters(current_params, df)
    upload_updated_parameters(posterior_params, latest_date=df.index.max())  # TODO: verify the date type is correct




