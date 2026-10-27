"""Tutar ve oran girişlerini Türkçe yazımla da okuyabilen yardımcı."""
import math
import re

_BINLIK_NOKTALI = re.compile(r"^[+-]?\d{1,3}(\.\d{3})+$")  # 1.500  12.500  1.250.000


def sayi_oku(metin):
    """
    '1500', '1500.5', '1500,50', '1.500,50', '1,500.50', '1.500' (bin beş yüz) -> float.
    Geçersiz ya da sonsuz değerlerde ValueError verir.
    """
    m = str(metin).strip().replace(" ", "").replace("TL", "").replace("₺", "")
    if "," in m and "." in m:
        # Hangisi sonda ise o ondalık ayracıdır, diğeri binlik ayracı
        m = m.replace(".", "").replace(",", ".") if m.rfind(",") > m.rfind(".") else m.replace(",", "")
    elif "," in m:
        m = m.replace(",", ".")
    elif _BINLIK_NOKTALI.match(m):
        m = m.replace(".", "")
    deger = float(m)
    if not math.isfinite(deger):
        raise ValueError(f"Geçersiz sayı: {metin}")
    return deger
