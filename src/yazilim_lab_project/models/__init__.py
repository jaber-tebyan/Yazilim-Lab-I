from typing import Annotated
from pydantic import Field
from yazilim_lab_project.models.results import (
    AddResourceResult,
    AddUserResult,
    PriceResult,
)

AnyResult = Annotated[
    AddUserResult.Any | AddResourceResult.Any,
    PriceResult.Any,
    Field(discriminator="command"),
]
