from datetime import datetime
from typing import Annotated
from pydantic import Field, PlainSerializer
from yazilim_lab_project.models.results import (
    AddResourceResult,
    AddUserResult,
    PriceResult,
    ReservationResult,
)

AnyResult = Annotated[
    AddUserResult.Any | AddResourceResult.Any | PriceResult.Any | ReservationResult.Any,
    Field(discriminator="command"),
]

