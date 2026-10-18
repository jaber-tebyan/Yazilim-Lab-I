from enum import StrEnum
from typing import Annotated, ClassVar, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field


class Error(StrEnum):
    ID_EXISTS = "ID_MEVCUT"
    UNDEFINED_VALUE = "TANIMSIZ_DEGER"
    INVALID_VALUE = "GECERSIZ_DEGER"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["kullanici_ekle"] = Field(alias="komut")


class Ok(_Base):
    status: Literal[Status.OK] = Field(default=Status.OK, alias="durum")


class Red(_Base):
    status: Literal[Status.RED] = Field(default=Status.RED, alias="durum")
    error_code: Error = Field(alias="kod")


Any = Annotated[Ok | Red, Field(discriminator="status")]
Variants: tuple[type, ...] = get_args(get_args(Any)[0])

__all__ = []
