from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field


class Error(StrEnum):
    ID_EXISTS = "ID_MEVCUT"
    UNDEFINED_VALUE = "TANIMSIZ_DEGER"


class Status(StrEnum):
    OK = "TAMAM"
    RED = "RED"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    no: int
    command: Literal["kaynak_ekle"] = Field(
        default="kaynak_ekle", validation_alias="komut", serialization_alias="komut"
    )


class Ok(_Base):
    status: Literal[Status.OK] = Field(
        default=Status.OK, validation_alias="durum", serialization_alias="durum"
    )


class Red(_Base):
    status: Literal[Status.RED] = Field(
        default=Status.RED, validation_alias="durum", serialization_alias="durum"
    )
    error_code: Error = Field(validation_alias="kod", serialization_alias="kod")


def new(no: int, error_code: Error | None = None) -> Ok | Red:
    if error_code == None:
        return Ok(no=no)
    else:
        return Red(no=no, error_code=error_code)


Variants = (Ok, Red)
Any = Annotated[Ok | Red, Field(discriminator="status")]

__all__ = []
