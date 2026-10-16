from datetime import datetime
from pydantic import BaseModel

from .baslangic import BakimPencere


class Command(BaseModel):
    komut: str


# {"komut":"kullanici_ekle","id":"u1","ad":"Ayşe Kaya","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80}


class KullaniciEkleCommand(Command):
    id: str
    ad: str
    rol: str
    sertifikalar: list[str]
    bakiye: int
    guvenilirlik: int


# {"komut":"kaynak_ekle","id":"YAZ-1","ad":"3B Yazıcı 1","tur":"YAZICI","izinli_roller":["OGRENCI"]}


class KaynakEkleCommand(Command):
    id: str
    ad: str
    tur: str
    izinli_roller: list[str]


# {"komut":"rezervasyon","kullanici":"u1","kaynak":"YAZ-1","baslangic":"2027-03-08T11:00","bitis":"2027-03-08T13:00"}


class RezervasyonCommand(Command):
    kullanici: str
    kaynak: str
    baslangic: datetime
    bitis: datetime


# {"komut":"fiyat","kullanici":"u3","kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}


class FiyatCommand(Command):
    kullanici: str
    kaynak: str
    baslangic: datetime
    bitis: datetime


# {"komut":"paket","kullanici":"u3","kalemler":[{"kaynak":"CIH-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"},{"kaynak":"ODA-1","baslangic":"2027-03-08T14:00","bitis":"2027-03-08T16:00"}]}


class PaketCommand(Command):
    kullanici: str
    kalemler: list[BakimPencere]


# {"komut":"bekleme","kullanici":"u2","kaynak":"YAZ-1","baslangic":"2027-03-08T12:00","bitis":"2027-03-08T13:00"}


class BeklemeCommand(Command):
    kullanici: str
    kaynak: str
    baslangic: datetime
    bitis: datetime


# {"komut":"saat","zaman":"2027-03-08T11:20"}


class SaatCommand(Command):
    zaman: datetime


# {"komut":"giris","rezervasyon":"r1"}


class GirisCommand(Command):
    rezervasyon: str


# {"komut":"iptal","rezervasyon":"r4"}


class IptalCommand(Command):
    rezervasyon: str


# {"komut":"sorgu","tur":"kullanici","id":"u2"}


class SorguCommand(Command):
    tur: str
    id: str
