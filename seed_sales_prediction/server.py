from datetime import datetime
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


def to_camel(string: str) -> str:
    words = string.split("_")
    camel_case = words[0] + "".join(word.capitalize() for word in words[1:])
    return camel_case


class NewData(BaseModel):
    """API Schema for new data."""

    direction: str = Field(..., example="OUTBOUND")
    order_id: Optional[str] = Field(None, example="145312343430657")
    order_secret_key: Optional[str] = Field(
        None, example="99assadda-12a4-44asdasdsad-asdasd9"
    )
    quantity: int = Field(..., example=10)
    created_at: datetime = Field(..., example=1606381833288)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class PredictedSales(BaseModel):
    expected_value: float = Field(
        ...,
        example=100.2,
        description="The expected number of sold seeds in one year, " "i.e 12 months.",
    )
    predictive_interval_95_percent: str = Field(
        ...,
        example="(150, 200)",
        description="The 95% predictive interval. I.e., there is a 0.95 probability that this interval will contain"
        " the correct number of sold seeds in one year,",
    )

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


@app.put(
    "/upload_data/{seed_id}",
    description="Upload new monthly data to update the predictive model.",
)
def upload_data(
    seed_id: str = Path(..., description="The id/name of the seed."),
    new_data: List[NewData] = Body(
        ...,
        description="The json url to get the data. Data should be complete per each month, i.e., "
        "should not upload half-month data only",
    ),
):
    latest_date = get_last_date_of_update(seed_id)
    df = pd.DataFrame([i.dict() for i in new_data])
    df = process_dataset(df)
    # only consider new data
    if latest_date:
        df = df[df.index > pd.to_datetime(latest_date, utc=True)]

    if df.shape[0] == 0:
        return

    current_params = get_prior_parameters(seed_id)
    posterior_params = get_updated_parameters(current_params, df)
    upload_updated_parameters(
        posterior_params, latest_date=df.index.max().to_period("M").to_timestamp("M")
    )


@app.get(
    "/predict_sales/{seed_id}",
    description="Predict sales for one whole year, i.e. 12 months.",
    response_model=PredictedSales,
)
def predict_sales(seed_id: str = Path(..., description="The id/name of the seed.")):
    current_params = get_prior_parameters(seed_id)
    predicted_sales = predict_one_year_sales(current_params)
    predictive_interval = (
        f"({predicted_sales.lower_bound_95}, {predicted_sales.upper_bound_95})"
    )
    return PredictedSales(
        expected_value=predicted_sales.expected_value,
        predictive_interval_95_percent=predictive_interval,
    )
