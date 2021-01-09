from datetime import time
from typing import List, Optional

import pandas as pd
from fastapi import Body, FastAPI, Path
from pydantic import BaseModel, Field

from seed_sales_prediction.funcs import (
    get_last_date_of_update,
    get_prior_parameters,
    get_updated_parameters,
    predict_one_year_sales,
    process_dataset,
    upload_updated_parameters,
)

app = FastAPI()


class NewData(BaseModel):
    """API Schema for new data."""

    direction: str
    order_id: Optional[str]
    order_secret_key: Optional[str]
    quantity: int
    created_at: time


class PredictedSales(BaseModel):
    expected_value: float = Field(
        ...,
        example=100.2,
        description="The expected number of sold seeds in one year, " "i.e 12 months.",
    )
    predictive_interval_95_percent: str = Field(
        ...,
        example="150-200",
        description="The 95% predictive interval. I.e., there is a 0.95 probability that this interval will contain"
        " the correct number of sold seeds in one year,",
    )


@app.put(
    "/upload_data/{seed_id}",
    description="Upload new monthly data to update the predictive model.",
)
def insert_tray(
    seed_id: str = Path(..., description="The id/name of the seed."),
    new_data: List[NewData] = Body(
        ...,
        description="The json url to get the data. Data should be complete per each month, i.e., "
        "should not upload half-month data only",
    ),
):
    latest_date = get_last_date_of_update(seed_id)
    df = pd.DataFrame(new_data)
    df = process_dataset(df)
    # only consider new data
    if latest_date:
        df = df[df.index > latest_date]  # TODO: check logic correct

    current_params = get_prior_parameters(seed_id)
    posterior_params = get_updated_parameters(current_params, df)
    upload_updated_parameters(
        posterior_params, latest_date=df.index.max().to_period('M').to_timestamp('M')
    )  # TODO: verify the date type is correct


@app.get(
    "/predict_sales/{seed_id}",
    description="Predict sales for one whole year, i.e. 12 months.",
)
def predict_sales(
    seed_id: str = Path(..., description="The id/name of the seed.")
) -> PredictedSales:
    current_params = get_prior_parameters(seed_id)
    predicted_sales = predict_one_year_sales(current_params)
    predictive_interval = (
        f"{predicted_sales.lower_bound_95}-{predicted_sales.upper_bound_95}"
    )
    return PredictedSales(
        expected_value=predicted_sales.expected_value,
        predictive_interval_95_percent=predictive_interval,
    )
