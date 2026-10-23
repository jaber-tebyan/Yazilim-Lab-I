from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.event import Event


class Error(StrEnum):
    CLOCK_BACK = "SAAT_GERI"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["saat"] = Field(
        default="saat", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )
    events: list[Event] = Field(
        default_factory=list,
        validation_alias="olaylar",
        serialization_alias="olaylar",
    )


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]
