from pydantic import BaseModel, Field

from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation


class AppState(BaseModel):
    config: InitialData

    reservations: list[Reservation] = Field(default_factory=list)
