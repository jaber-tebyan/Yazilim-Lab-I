from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field


class Error(StrEnum):
    NOT_FOUND = "BULUNAMADI"
    TIME_STEP_ERROR = "ZAMAN_ADIMI_HATASI"
    PAST_TIME = "GECMIS_ZAMAN"
    OUT_OF_WORKING_HOURS = "CALISMA_SAATI_DISI"
    TIME_LIMIT = "SURE_SINIRI"
    FUTURE_DATE_LIMIT = "ILERI_TARIH_SINIRI"
    NO_ROLE_PERMISSION = "ROL_IZNI_YOK"
    NO_CERTIFICATE = "SERTIFIKA_YOK"
    MAINTENANCE = "BAKIM"
    CONSECUTIVE_USE = "ARDISIK_KULLANIM"
    WAITING_UNNECESSARY = "BEKLEME_GEREKSIZ"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["bekleme"] = Field(
        default="bekleme", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )
    waitlist_id: str = Field(
        validation_alias="bekleme_id", serialization_alias="bekleme_id"
    )
    position: int = Field(validation_alias="sira", serialization_alias="sira")


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]
