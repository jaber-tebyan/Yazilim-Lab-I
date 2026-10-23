from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models import reservation


class Error(StrEnum):
    NOT_FOUND = "BULUNAMADI"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class ReservationRow(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    id: str
    resource: str = Field(validation_alias="kaynak", serialization_alias="kaynak")
    start: str = Field(validation_alias="baslangic", serialization_alias="baslangic")
    end: str = Field(validation_alias="bitis", serialization_alias="bitis")
    status: reservation.State = Field(
        validation_alias="durum", serialization_alias="durum"
    )
    price: int = Field(validation_alias="ucret", serialization_alias="ucret")


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
    balance: int = Field(validation_alias="bakiye", serialization_alias="bakiye")
    reliability: int = Field(
        validation_alias="guvenilirlik", serialization_alias="guvenilirlik"
    )
    reservations: list[ReservationRow] = Field(
        default_factory=list,
        validation_alias="rezervasyonlar",
        serialization_alias="rezervasyonlar",
    )


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]
