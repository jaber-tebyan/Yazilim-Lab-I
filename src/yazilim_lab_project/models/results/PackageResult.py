from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field


class Error(StrEnum):
    NOT_FOUND = "BULUNAMADI"
    PACKAGE_SIZE = "PAKET_BOYUTU"
    LOW_RELIABILITY = "GUVENILIRLIK_DUSUK"
    PACKAGE_REJECTED = "PAKET_RED"
    INTRA_PACKAGE_INTERSECTION = "PAKET_ICI_KESISME"
    INSUFFICIENT_BALANCE = "BAKIYE_YETERSIZ"


class ItemError(StrEnum):
    NOT_FOUND = "BULUNAMADI"
    TIME_STEP_ERROR = "ZAMAN_ADIMI_HATASI"
    PAST_TIME = "GECMIS_ZAMAN"
    OUT_OF_WORKING_HOURS = "CALISMA_SAATI_DISI"
    DURATION_LIMIT = "SURE_SINIRI"
    FUTURE_DATE_LIMIT = "ILERI_TARIH_SINIRI"
    NO_ROLE_PERMISSION = "ROL_IZNI_YOK"
    NO_CERTIFICATE = "SERTIFIKA_YOK"
    MAINTENANCE = "BAKIM"
    INTERSECTION = "KESISME"
    PREPARATION_VIOLATION = "HAZIRLIK_IHLALI"
    CONSECUTIVE_USE = "ARDISIK_KULLANIM"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class Item(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    index: int = Field(validation_alias="sira", serialization_alias="sira")
    status: Status = Field(validation_alias="durum", serialization_alias="durum")
    error_code: ItemError | None = Field(
        default=None, validation_alias="kod", serialization_alias="kod"
    )


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["paket"] = Field(
        default="paket", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )
    package_id: str = Field(validation_alias="paket_id", serialization_alias="paket_id")
    reservations: list[str] = Field(
        validation_alias="rezervasyonlar", serialization_alias="rezervasyonlar"
    )
    prices: list[int] = Field(
        validation_alias="ucretler", serialization_alias="ucretler"
    )
    total: int = Field(validation_alias="toplam", serialization_alias="toplam")
    balance: int = Field(validation_alias="bakiye", serialization_alias="bakiye")


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")
    items: list[Item] = Field(
        default_factory=list,
        validation_alias="kalemler",
        serialization_alias="kalemler",
    )


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]
