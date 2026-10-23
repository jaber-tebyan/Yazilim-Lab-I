from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.event import AutoAssign


class Error(StrEnum):
    NOT_FOUND = "BULUNAMADI"
    STATE_ERROR = "DURUM_HATASI"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["iptal"] = Field(
        default="iptal", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )
    refund: int = Field(validation_alias="iade", serialization_alias="iade")
    balance: int = Field(validation_alias="bakiye", serialization_alias="bakiye")
    reliability: int = Field(
        validation_alias="guvenilirlik", serialization_alias="guvenilirlik"
    )
    events: list[AutoAssign] = Field(
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
