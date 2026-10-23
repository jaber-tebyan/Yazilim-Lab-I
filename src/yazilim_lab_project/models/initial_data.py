from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models import Timestamp


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)


class ResourceType(_Base):
    preparation_min: int = Field(
        validation_alias="hazirlik_dk", serialization_alias="hazirlik_dk"
    )
    base_fee: int = Field(
        validation_alias="temel_ucret", serialization_alias="temel_ucret"
    )
    energy_intensive: bool = Field(
        validation_alias="enerji_yogun", serialization_alias="enerji_yogun"
    )
    certificate: str | None = Field(
        validation_alias="sertifika", serialization_alias="sertifika"
    )


class Role(_Base):
    weekly_quota: int = Field(
        validation_alias="haftalik_kota", serialization_alias="haftalik_kota"
    )
    future_day: int = Field(
        validation_alias="ileri_gun", serialization_alias="ileri_gun"
    )
    max_duration_min: int = Field(
        validation_alias="azami_sure_dk", serialization_alias="azami_sure_dk"
    )


class Resource(_Base):
    id: str
    name: str = Field(validation_alias="ad", serialization_alias="ad")
    type: str = Field(validation_alias="tur", serialization_alias="tur")
    allowed_roles: list[str] = Field(
        validation_alias="izinli_roller", serialization_alias="izinli_roller"
    )


class MaintenanceWindow(_Base):
    resource: str = Field(validation_alias="kaynak", serialization_alias="kaynak")
    start: Timestamp = Field(
        validation_alias="baslangic", serialization_alias="baslangic"
    )
    end: Timestamp = Field(validation_alias="bitis", serialization_alias="bitis")


class User(_Base):
    id: str
    name: str = Field(validation_alias="ad", serialization_alias="ad")
    role: str = Field(validation_alias="rol", serialization_alias="rol")
    certificates: list[str] = Field(
        validation_alias="sertifikalar", serialization_alias="sertifikalar"
    )
    balance: int = Field(validation_alias="bakiye", serialization_alias="bakiye")
    reliability: int = Field(
        validation_alias="guvenilirlik", serialization_alias="guvenilirlik"
    )


class InitialData(_Base):
    time: Timestamp = Field(validation_alias="saat", serialization_alias="saat")
    resource_types: dict[str, ResourceType] = Field(
        validation_alias="kaynak_turleri", serialization_alias="kaynak_turleri"
    )
    roles: dict[str, Role] = Field(
        validation_alias="roller", serialization_alias="roller"
    )
    resources: list[Resource] = Field(
        validation_alias="kaynaklar", serialization_alias="kaynaklar"
    )
    maintenance_windows: list[MaintenanceWindow] = Field(
        validation_alias="bakim_pencereleri", serialization_alias="bakim_pencereleri"
    )
    users: list[User] = Field(
        validation_alias="kullanicilar", serialization_alias="kullanicilar"
    )

    @staticmethod
    def empty():
        return InitialData(
            time=datetime.now(),
            resource_types={},
            roles={},
            resources=[],
            maintenance_windows=[],
            users=[],
        )
