from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, Field

# {"komut":"kullanici_ekle","id":"u1","ad":"Ayşe Kaya","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80}


class KullaniciEkleCommand(BaseModel):
    komut: Literal["kullanici_ekle"]
    id: str
    ad: str
    rol: str
    sertifikalar: list[str]
    bakiye: int
    guvenilirlik: int


# {"komut":"kaynak_ekle","id":"YAZ-1","ad":"3B Yazıcı 1","tur":"YAZICI","izinli_roller":["OGRENCI"]}


class KaynakEkleCommand(BaseModel):
    komut: Literal["kaynak_ekle"]
    id: str
    ad: str
    tur: str
    izinli_roller: list[str]


# {"komut":"rezervasyon","kullanici":"u1","kaynak":"YAZ-1","baslangic":"2027-03-08T11:00","bitis":"2027-03-08T13:00"}


class RezervasyonCommand(BaseModel):
    komut: Literal["rezervasyon"]
    kullanici: str
    kaynak: str
    baslangic: datetime
    bitis: datetime


# {"komut":"fiyat","kullanici":"u3","kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}


class FiyatCommand(BaseModel):
    komut: Literal["fiyat"]
    kullanici: str
    kaynak: str
    baslangic: datetime
    bitis: datetime


# {"komut":"paket","kullanici":"u3","kalemler":[{"kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"},{"kaynak":"ODA-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}]}


class ReservationRequests(BaseModel):
    kaynak: str
    baslangic: datetime
    bitis: datetime


class PaketCommand(BaseModel):
    komut: Literal["paket"]
    kullanici: str
    kalemler: list[ReservationRequests]


# {"komut":"bekleme","kullanici":"u2","kaynak":"YAZ-1","baslangic":"2027-03-08T12:00","bitis":"2027-03-08T13:00"}


class BeklemeCommand(BaseModel):
    komut: Literal["bekleme"]
    kullanici: str
    kaynak: str
    baslangic: datetime
    bitis: datetime


# {"komut":"saat","zaman":"2027-03-08T11:20"}


class SaatCommand(BaseModel):
    komut: Literal["saat"]
    zaman: datetime


# {"komut":"giris","rezervasyon":"r1"}


class GirisCommand(BaseModel):
    komut: Literal["giris"]
    rezervasyon: str


# {"komut":"iptal","rezervasyon":"r4"}


class IptalCommand(BaseModel):
    komut: Literal["iptal"]
    rezervasyon: str


# {"komut":"sorgu","tur":"kullanici","id":"u2"}


class SorguCommand(BaseModel):
    komut: Literal["sorgu"]
    tur: str
    id: str


AnyCommand = Annotated[
    KullaniciEkleCommand
    | KaynakEkleCommand
    | RezervasyonCommand
    | FiyatCommand
    | PaketCommand
    | BeklemeCommand
    | SaatCommand
    | GirisCommand
    | IptalCommand
    | SorguCommand,
    Field(discriminator="komut"),
]
