from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models import reservation


class Error(StrEnum):
    NOT_FOUND = "BULUNAMADI"
    STATE_ERROR = "DURUM_HATASI"
    OUTSIDE_USE_WINDOW = "GIRIS_PENCERESI_DISI"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["giris"] = Field(
        default="giris", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )
    new_status: reservation.State = Field(
        validation_alias="yeni_durum", serialization_alias="yeni_durum"
    )


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]
