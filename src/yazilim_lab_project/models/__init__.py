from typing import Annotated
from pydantic import Field
from yazilim_lab_project.models.results import AddResourceResult, AddUserResult

AnyResult = Annotated[
    AddUserResult.Any | AddResourceResult.Any, Field(discriminator="command")
]
