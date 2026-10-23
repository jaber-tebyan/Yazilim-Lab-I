from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.app_state import Timestamp


class Error(StrEnum):
    NOT_FOUND = "BULUNAMADI"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class OccupancyType(StrEnum):
    RESERVATION = "REZERVASYON"
    MAINTENANCE = "BAKIM"


class OccupancyRow(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    start: Timestamp = Field(
        validation_alias="baslangic", serialization_alias="baslangic"
    )
    end: Timestamp = Field(validation_alias="bitis", serialization_alias="bitis")
    type: OccupancyType = Field(validation_alias="tur", serialization_alias="tur")
    reservation: str | None = Field(
        default=None,
        validation_alias="rezervasyon",
        serialization_alias="rezervasyon",
    )


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["sorgu"] = Field(
        default="sorgu", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )
    occupancy: list[OccupancyRow] = Field(
        default_factory=list,
        validation_alias="doluluk",
        serialization_alias="doluluk",
    )


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]
