"""Liste ekranlarındaki arama kutuları için Türkçe karakter ve büyük/küçük harf duyarsız eşleştirme."""

# Türkçe harfleri ve şapkalı harfleri düz Latin karşılıklarına indirir; "İ/I/ı/i" hepsi "i" olur.
# (str.lower() "İ" harfini "i̇" yapar, SQLite LIKE ise Türkçe harflerde büyük/küçük eşleştiremez.)
_KATLAMA = str.maketrans({
    "İ": "i", "I": "i", "ı": "i",
    "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g", "Ü": "u", "ü": "u",
    "Ö": "o", "ö": "o", "Ç": "c", "ç": "c",
    "Â": "a", "â": "a", "Î": "i", "î": "i", "Û": "u", "û": "u",
})


def arama_anahtari(deger):
    """'MÜHENDİSLİK', 'mühendislik' ve 'muhendislik' aynı anahtara dönüşür."""
    if deger is None:
        return ""
    return str(deger).translate(_KATLAMA).lower()


def arama_kaydi(*alanlar):
    """
    Bir satırın aranacak alanlarını bir kez katlayıp saklar (binlerce satırda her tuşta yeniden yapılmasın).
    Alanlar satır sonu ile ayrılır: arama kelimeleri boşluk/satır sonu içermediği için iki alana taşamaz.
    """
    metin = arama_anahtari("\n".join("" if alan is None else str(alan) for alan in alanlar))
    return metin, metin.replace(" ", "")


def arama_sorgusu(aranan):
    kelimeler = arama_anahtari(aranan).split()
    return kelimeler, "".join(kelimeler)


def kayit_eslesir(sorgu, kayit):
    """arama_sorgusu() ile arama_kaydi() çıktılarını karşılaştırır; kurallar eslesir() ile aynıdır."""
    kelimeler, bitisik = sorgu
    if not kelimeler:
        return True
    metin, bitisik_metin = kayit
    return all(kelime in metin for kelime in kelimeler) or bitisik in bitisik_metin


def eslesir(aranan, *alanlar):
    """
    Aranan metindeki her kelime alanlardan birinde geçiyorsa True döner (boş arama her şeyle eşleşir).
    Türkçe harf / büyük-küçük harf farkı yok sayılır; '80ak549' yazınca '80 AK 549' plakası da bulunur.
    """
    return kayit_eslesir(arama_sorgusu(aranan), arama_kaydi(*alanlar))
