from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, Field

from yazilim_lab_project.models.config import Timestamp

# {"komut":"kullanici_ekle","id":"u1","ad":"Ayşe Kaya","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80}


class AddUserCommand(BaseModel):
    command: Literal["kullanici_ekle"] = Field(alias="komut")
    id: str
    name: str = Field(alias="ad")
    role: str = Field(alias="rol")
    certificates: list[str] = Field(alias="sertifikalar")
    balance: int = Field(alias="bakiye")
    reliability: int = Field(alias="guvenilirlik")


# {"komut":"kaynak_ekle","id":"YAZ-1","ad":"3B Yazıcı 1","tur":"YAZICI","izinli_roller":["OGRENCI"]}
class AddResourceCommand(BaseModel):
    command: Literal["kaynak_ekle"] = Field(alias="komut")
    id: str
    name: str = Field(alias="ad")
    type: str = Field(alias="tur")
    allowed_roles: list[str] = Field(alias="izinli_roller")


# {"komut":"rezervasyon","kullanici":"u1","kaynak":"YAZ-1","baslangic":"2027-03-08T11:00","bitis":"2027-03-08T13:00"}
class ReservationCommand(BaseModel):
    command: Literal["rezervasyon"] = Field(alias="komut")
    user: str = Field(alias="kullanici")
    resource: str = Field(alias="kaynak")
    start: Timestamp = Field(alias="baslangic")
    end: Timestamp = Field(alias="bitis")


# {"komut":"fiyat","kullanici":"u3","kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}
class PriceCommand(BaseModel):
    command: Literal["fiyat"] = Field(alias="komut")
    user: str = Field(alias="kullanici")
    resource: str = Field(alias="kaynak")
    start: Timestamp = Field(alias="baslangic")
    end: Timestamp = Field(alias="bitis")


# {"komut":"paket","kullanici":"u3","kalemler":[{"kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"},{"kaynak":"ODA-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}]}
class ReservationRequests(BaseModel):
    resource: str = Field(alias="kaynak")
    start: Timestamp = Field(alias="baslangic")
    end: Timestamp = Field(alias="bitis")


class PackageCommand(BaseModel):
    command: Literal["paket"] = Field(alias="komut")
    user: str = Field(alias="kullanici")
    items: list[ReservationRequests] = Field(alias="kalemler")


# {"komut":"bekleme","kullanici":"u2","kaynak":"YAZ-1","baslangic":"2027-03-08T12:00","bitis":"2027-03-08T13:00"}
class WaitingListCommand(BaseModel):
    command: Literal["bekleme"] = Field(alias="komut")
    user: str = Field(alias="kullanici")
    resource: str = Field(alias="kaynak")
    start: Timestamp = Field(alias="baslangic")
    end: Timestamp = Field(alias="bitis")


# {"komut":"saat","zaman":"2027-03-08T11:20"}
class ClockCommand(BaseModel):
    command: Literal["saat"] = Field(alias="komut")
    time: Timestamp = Field(alias="zaman")


# {"komut":"giris","rezervasyon":"r1"}
class CheckInCommand(BaseModel):
    command: Literal["giris"] = Field(alias="komut")
    reservation: str = Field(alias="rezervasyon")


# {"komut":"iptal","rezervasyon":"r4"}
class CancelCommand(BaseModel):
    command: Literal["iptal"] = Field(alias="komut")
    reservation: str = Field(alias="rezervasyon")


# {"komut":"sorgu","tur":"kullanici","id":"u2"}
class QueryUserCommand(BaseModel):
    command: Literal["sorgu"] = Field(alias="komut")
    type: Literal["kaynak"] = Field(alias="tur")
    id: str


class QueryResourceCommand(BaseModel):
    command: Literal["sorgu"] = Field(alias="komut")
    type: Literal["kullanici"] = Field(alias="tur")
    id: str
    day: date = Field(alias="gun")


AnyCommand = Annotated[
    AddUserCommand
    | AddResourceCommand
    | ReservationCommand
    | PriceCommand
    | PackageCommand
    | WaitingListCommand
    | ClockCommand
    | CheckInCommand
    | CancelCommand
    | QueryUserCommand
    | QueryResourceCommand,
    Field(discriminator="command"),
]
