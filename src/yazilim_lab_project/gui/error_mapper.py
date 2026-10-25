"""Error codes to Turkish explanations mapping according to Yaz_Lab_I.txt."""

ERROR_DESCRIPTIONS: dict[str, str] = {
    "BULUNAMADI": "Kullanıcı veya kaynak sistemde bulunamadı.",
    "ZAMAN_ADIMI_HATASI": "Zaman adımı hatalı (15 dakikalık adımlara oturmuyor veya bitiş başlangıçtan önce).",
    "GECMIS_ZAMAN": "Başlangıç zamanı simüle saatten önce olamaz.",
    "CALISMA_SAATI_DISI": "Talep 08:00–22:00 çalışma saatleri dışında veya gün aşımı var.",
    "SURE_SINIRI": "Rezervasyon süresi en az 30 dk veya rolün izin verdiği azami süreden fazla.",
    "ILERI_TARIH_SINIRI": "Rolün ileri tarih rezervasyon sınırı aşıldı (güvenilirlik düşükse 1 gün).",
    "ROL_IZNI_YOK": "Kullanıcının rolü bu kaynağı rezerve etmek için yetkili değil.",
    "SERTIFIKA_YOK": "Bu kaynağın gerektirdiği sertifikaya sahip değilsiniz.",
    "BAKIM": "Talep edilen zaman aralığı planlı bir bakım penceresiyle kesişiyor.",
    "KESISME": "Talep edilen zaman aralığı mevcut bir rezervasyonla çakışıyor.",
    "HAZIRLIK_IHLALI": "İki kullanım arasındaki zorunlu hazırlık/temizlik süresi ihlal edildi.",
    "ARDISIK_KULLANIM": "Aynı kullanıcının aynı kaynakta ardışık iki rezervasyonu arasında en az 60 dk boşluk olmalıdır.",
    "BAKIYE_YETERSIZ": "Hesabınızdaki Kaynak Puan (KP) bakiyesi bu rezervasyon için yetersiz.",
    "BEKLEME_GEREKSIZ": "Zaman aralığı zaten müsait, bekleme listesi açılamaz.",
    "GIRIS_PENCERESI_DISI": "Giriş işlemi sadece başlangıçtan 10 dk önce ile 15 dk sonra yapılabilir.",
    "DURUM_HATASI": "Rezervasyonun mevcut durumu bu işlem için uygun değil.",
    "SAAT_GERI": "Simüle saat geriye alınamaz.",
    "ID_MEVCUT": "Bu ID'ye sahip bir kullanıcı veya kaynak zaten mevcut.",
    "TANIMSIZ_DEGER": "Belirtilen rol veya kaynak türü sistemde tanımlı değil.",
    "GECERSIZ_DEGER": "Girilen değer geçersiz veya sayı tam sayı değil.",
    "PAKET_BOYUTU": "Paket en az 2, en fazla 4 kalemden oluşmalıdır.",
    "GUVENILIRLIK_DUSUK": "Güvenilirlik puanı 50'nin altında olduğu için paket rezervasyon yapılamaz.",
    "PAKET_RED": "Paketteki en az bir kalem kurallara takıldı.",
    "PAKET_ICI_KESISME": "Paket içindeki kalemler birbiriyle veya hazırlık/ardışık kurallarıyla çakışıyor.",
}


def get_error_desc(code: str) -> str:
    return ERROR_DESCRIPTIONS.get(code, f"İşlem reddedildi ({code}).")
