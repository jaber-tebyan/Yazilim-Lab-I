from typing import Annotated
from pydantic import Field
from yazilim_lab_project.models.results import AddUserResult

AnyResult = Annotated[AddUserResult.Any, Field(discriminator="command")]
