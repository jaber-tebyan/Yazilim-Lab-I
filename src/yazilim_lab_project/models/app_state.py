from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer

from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation


class AppState(BaseModel):
    config: InitialData

    reservations: list[Reservation] = Field(default_factory=list)


Timestamp = Annotated[
    datetime,
    PlainSerializer(lambda d: d.strftime("%Y-%m-%dT%H:%M"), return_type=str),
]
