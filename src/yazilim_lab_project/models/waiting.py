from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.config import Timestamp


class WaitingEntry(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="id", validation_alias="id")
    user: str = Field(serialization_alias="kullanici", validation_alias="kullanici")
    resource: str = Field(serialization_alias="kaynak", validation_alias="kaynak")
    start: Timestamp = Field(
        serialization_alias="baslangic", validation_alias="baslangic"
    )
    end: Timestamp = Field(serialization_alias="bitis", validation_alias="bitis")
    registered_at: Timestamp = Field(
        serialization_alias="kayit_saati", validation_alias="kayit_saati"
    )
