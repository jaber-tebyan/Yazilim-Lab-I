from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.app_state import Timestamp


# TODO: Change State name to something else for possible name collisions with App_State
class State(StrEnum):
    APPROVED = "ONAYLI"
    IN_USE = "KULLANIMDA"
    COMPLETED = "TAMAMLANDI"
    CANCELLED = "IPTAL"
    DID_NOT_ARRIVE = "GELMEDI"


class Reservation(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="id", validation_alias="id")
    user: str = Field(serialization_alias="kullanici", validation_alias="kullanici")
    resource: str = Field(serialization_alias="kaynak", validation_alias="kaynak")
    start: Timestamp = Field(
        serialization_alias="baslangic", validation_alias="baslangic"
    )
    # TODO: Use custom formated datetime
    # Because pydantic default datetime dumps seconds as well
    end: Timestamp = Field(serialization_alias="bitis", validation_alias="bitis")
    price: int = Field(serialization_alias="ucret", validation_alias="ucret")
    state: State = Field(serialization_alias="durum", validation_alias="durum")
    package: str | None = Field(
        default=None, serialization_alias="paket", validation_alias="paket"
    )
