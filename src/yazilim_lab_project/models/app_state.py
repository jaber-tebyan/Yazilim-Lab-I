from pydantic import BaseModel, Field

from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.waiting import WaitingEntry


class AppState(BaseModel):
    config: InitialData

    reservations: list[Reservation] = Field(default_factory=list)
    waiting_list: list[WaitingEntry] = Field(default_factory=list)
    next_waiting_id: int = 0
