from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.models.config import Timestamp

# {"komut":"kullanici_ekle","id":"u1","ad":"Ayşe Kaya","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80}


class _Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class AddUserCommand(_Base):
    command: Literal["kullanici_ekle"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
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


# {"komut":"kaynak_ekle","id":"YAZ-1","ad":"3B Yazıcı 1","tur":"YAZICI","izinli_roller":["OGRENCI"]}
class AddResourceCommand(_Base):
    command: Literal["kaynak_ekle"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    id: str
    name: str = Field(validation_alias="ad", serialization_alias="ad")
    type: str = Field(validation_alias="tur", serialization_alias="tur")
    allowed_roles: list[str] = Field(
        validation_alias="izinli_roller", serialization_alias="izinli_roller"
    )


# {"komut":"rezervasyon","kullanici":"u1","kaynak":"YAZ-1","baslangic":"2027-03-08T11:00","bitis":"2027-03-08T13:00"}
class ReservationCommand(_Base):
    command: Literal["rezervasyon"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    user: str = Field(validation_alias="kullanici", serialization_alias="kullanici")
    resource: str = Field(validation_alias="kaynak", serialization_alias="kaynak")
    start: Timestamp = Field(
        validation_alias="baslangic", serialization_alias="baslangic"
    )
    end: Timestamp = Field(validation_alias="bitis", serialization_alias="bitis")


# {"komut":"fiyat","kullanici":"u3","kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}
class PriceCommand(_Base):
    command: Literal["fiyat"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    user: str = Field(validation_alias="kullanici", serialization_alias="kullanici")
    resource: str = Field(validation_alias="kaynak", serialization_alias="kaynak")
    start: Timestamp = Field(
        validation_alias="baslangic", serialization_alias="baslangic"
    )
    end: Timestamp = Field(validation_alias="bitis", serialization_alias="bitis")


# {"komut":"paket","kullanici":"u3","kalemler":[{"kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"},{"kaynak":"ODA-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}]}
class ReservationRequests(_Base):
    resource: str = Field(validation_alias="kaynak", serialization_alias="kaynak")
    start: Timestamp = Field(
        validation_alias="baslangic", serialization_alias="baslangic"
    )
    end: Timestamp = Field(validation_alias="bitis", serialization_alias="bitis")


class PackageCommand(_Base):
    command: Literal["paket"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    user: str = Field(validation_alias="kullanici", serialization_alias="kullanici")
    items: list[ReservationRequests] = Field(
        validation_alias="kalemler", serialization_alias="kalemler"
    )


# {"komut":"bekleme","kullanici":"u2","kaynak":"YAZ-1","baslangic":"2027-03-08T12:00","bitis":"2027-03-08T13:00"}
class WaitingListCommand(_Base):
    command: Literal["bekleme"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    user: str = Field(validation_alias="kullanici", serialization_alias="kullanici")
    resource: str = Field(validation_alias="kaynak", serialization_alias="kaynak")
    start: Timestamp = Field(
        validation_alias="baslangic", serialization_alias="baslangic"
    )
    end: Timestamp = Field(validation_alias="bitis", serialization_alias="bitis")


# {"komut":"saat","zaman":"2027-03-08T11:20"}
class ClockCommand(_Base):
    command: Literal["saat"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    time: Timestamp = Field(validation_alias="zaman", serialization_alias="zaman")


# {"komut":"giris","rezervasyon":"r1"}
class EntryCommand(_Base):
    command: Literal["giris"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    reservation: str = Field(
        validation_alias="rezervasyon", serialization_alias="rezervasyon"
    )


# {"komut":"cikis","rezervasyon":"r1"}
class ExitCommand(_Base):
    command: Literal["cikis"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    reservation: str = Field(
        validation_alias="rezervasyon", serialization_alias="rezervasyon"
    )


# {"komut":"iptal","rezervasyon":"r4"}
class CancelCommand(_Base):
    command: Literal["iptal"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    reservation: str = Field(
        validation_alias="rezervasyon", serialization_alias="rezervasyon"
    )


# {"komut":"sorgu","tur":"kullanici","id":"u2"}
class QueryUserCommand(_Base):
    command: Literal["sorgu"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    type: Literal["kullanici"] = Field(
        validation_alias="tur", serialization_alias="tur"
    )
    id: str


class QueryResourceCommand(_Base):
    command: Literal["sorgu"] = Field(
        validation_alias="komut", serialization_alias="komut"
    )
    type: Literal["kaynak"] = Field(validation_alias="tur", serialization_alias="tur")
    id: str
    day: date = Field(validation_alias="gun", serialization_alias="gun")


QueryCommand = Annotated[
    QueryUserCommand | QueryResourceCommand, Field(discriminator="type")
]


AnyCommand = Annotated[
    AddUserCommand
    | AddResourceCommand
    | ReservationCommand
    | PriceCommand
    | PackageCommand
    | WaitingListCommand
    | ClockCommand
    | EntryCommand
    | ExitCommand
    | CancelCommand
    | QueryCommand,
    Field(discriminator="command"),
]
