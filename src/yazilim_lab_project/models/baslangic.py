from datetime import datetime
from pydantic import BaseModel


class KaynakTur(BaseModel):
    hazirlik_dk: int
    temel_ucret: int
    enerji_yogun: bool
    sertifika: str | None


class Roll(BaseModel):
    haftalik_kota: int
    ileri_gun: int
    azami_sure_dk: int


class Kaynak(BaseModel):
    id: str
    ad: str
    tur: str
    izinli_roller: list[str]


class BakimPencere(BaseModel):
    kaynak: str
    baslangic: datetime  # isoformat datetime
    bitis: datetime  # isoformat datetime


class Kullanici(BaseModel):
    id: str
    ad: str
    rol: str
    sertifikalar: list[str]
    bakiye: int
    guvenilirlik: int


class InitialData(BaseModel):
    saat: datetime
    kaynak_turleri: dict[str, KaynakTur]
    roller: dict[str, Roll]
    kaynaklar: list[Kaynak]
    bakim_pencereleri: list[BakimPencere]
    kullanicilar: list[Kullanici]
