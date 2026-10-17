from datetime import datetime
from pydantic import BaseModel, Field


class ResourceType(BaseModel):
    preparation_min: int = Field(alias="hazirlik_dk")
    base_fee: int = Field(alias="temel_ucret")
    energy_intensive: bool = Field(alias="enerji_yogun")
    certificate: str | None = Field(alias="sertifika")


class Role(BaseModel):
    weekly_quota: int = Field(alias="haftalik_kota")
    future_day: int = Field(alias="ileri_gun")
    max_duration_min: int = Field(alias="azami_sure_dk")


class Resource(BaseModel):
    id: str
    name: str = Field(alias="ad")
    type: str = Field(alias="tur")
    permitted_roles: list[str] = Field(alias="izinli_roller")


class MaintenanceWindow(BaseModel):
    resource: str = Field(alias="kaynak")
    start: datetime = Field(alias="baslangic")
    end: datetime = Field(alias="bitis")


class User(BaseModel):
    id: str
    name: str = Field(alias="ad")
    role: str = Field(alias="rol")
    certificates: list[str] = Field(alias="sertifikalar")
    balance: int = Field(alias="bakiye")
    reliability: int = Field(alias="guvenilirlik")


class InitialData(BaseModel):
    time: datetime = Field(alias="saat")
    resource_types: dict[str, ResourceType] = Field(alias="kaynak_turleri")
    roles: dict[str, Role] = Field(alias="roller")
    resources: list[Resource] = Field(alias="kaynaklar")
    maintenance_windows: list[MaintenanceWindow] = Field(alias="bakim_pencereleri")
    users: list[User] = Field(alias="kullanicilar")

    @staticmethod
    def empty():
        return InitialData(
            saat=datetime.now(),
            kaynak_turleri={},
            roller={},
            kaynaklar=[],
            bakim_pencereleri=[],
            kullanicilar=[],
        )
