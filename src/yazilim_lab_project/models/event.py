from enum import StrEnum
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    WEEKLY_RESET = "HAFTALIK_SIFIRLAMA"
    COMPLETED = "TAMAMLANDI"
    NO_SHOW = "GELMEDI"
    AUTO_ASSIGN = "OTOMATIK_ATAMA"


class _EventBase(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    time: str = Field(validation_alias="zaman", serialization_alias="zaman")


class AutoAssign(_EventBase):
    type: Literal[EventType.AUTO_ASSIGN] = Field(
        default=EventType.AUTO_ASSIGN,
        validation_alias="tur",
        serialization_alias="tur",
    )
    waitlist: str = Field(validation_alias="bekleme", serialization_alias="bekleme")
    reservation: str = Field(
        validation_alias="rezervasyon", serialization_alias="rezervasyon"
    )
    user: str = Field(validation_alias="kullanici", serialization_alias="kullanici")
    price: int = Field(validation_alias="ucret", serialization_alias="ucret")
    balance: int = Field(validation_alias="bakiye", serialization_alias="bakiye")
