# encoding:utf-8
"""
İş emri, fatura ve teklif PDF'leri.

ReportLab Platypus ile akışkan sayfa düzeni kullanılır: kalem sayısı ne olursa olsun tablo
sayfalara bölünür, başlık satırı her sayfada tekrar eder, uzun açıklamalar hücre içinde alt
satıra kayar; toplamlar ve imza alanı bölünmeden bir sonraki sayfaya taşınır. Fontlar sadece
kullanılan karakterlerle gömüldüğü için dosyalar küçüktür.
"""
import datetime
import logging
import os
import sys
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import lru_cache
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, PageTemplate, Paragraph, Spacer, Table, TableStyle
)

# Belgelerin üst bilgisinde görünen firma bilgileri
FIRMA = {
    "ad": "CLASSİC CAR",
    "adres": "Yeşiloba Mah. 46257 Sk. Adana Otosanayi Sitesi M Blok No:7/13 İç Kapı No:Z09 Seyhan/Adana",
    "telefon": "0538 832 47 25",
}

KOYU = colors.HexColor("#1F3A5F")
ACIK = colors.HexColor("#EEF2F7")
ZEBRA = colors.HexColor("#F7F9FB")
CIZGI = colors.HexColor("#C5CED9")
INCE_CIZGI = colors.HexColor("#E3E8EE")
GRI_YAZI = colors.HexColor("#5B6573")
LOGO_RENGI = colors.HexColor("#2B2B2B")

SAYFA_GENISLIK, SAYFA_YUKSEKLIK = A4
KENAR = 14 * mm
UST_BOSLUK = 38 * mm
ALT_BOSLUK = 18 * mm
ICERIK_GENISLIK = SAYFA_GENISLIK - 2 * KENAR

_MAX_HUCRE = 1500  # Tek hücre sayfadan uzun olamasın diye üst sınır (karakter)


def _resource_path(relative_path):
    """PyInstaller ile paketlenmiş uygulamada da dosya yolunu bulur."""
    return os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(".")), relative_path)


_WIN_FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
# Windows'un Arial'ı Türkçe karakterleri içerir ve 22 MB'lık gömülü fonttan ~20 kat hızlı yüklenir
_FONT_ADAYLARI = [
    (os.path.join(_WIN_FONTS, "arial.ttf"), os.path.join(_WIN_FONTS, "arialbd.ttf")),
    (_resource_path("arial-unicode-ms.ttf"), _resource_path("arial-unicode-ms-bold.ttf")),
]
_LOGO_FONT_ADAYLARI = [os.path.join(_WIN_FONTS, "cambria.ttc"), os.path.join(_WIN_FONTS, "times.ttf")]
# Latin, Yunan, Kiril harfleri ile noktalama, para birimi ve simgeler
_FONT_ARALIKLARI = [(0x20, 0x52F), (0x1E00, 0x1EFF), (0x2000, 0x2BFF)]
_FONT_ISLEME_SURUMU = 1


def _font_onbellek_klasoru():
    taban = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
    return os.path.join(taban, "OTO-SERVIS", "fontlar")


def _tek_parca_font(yol):
    """
    Fontun Ç, Ü, Ö, Ş, İ gibi birleşik (harf + işaret) gliflerini tek parça hale getirir ve hinting
    komutlarını kaldırır; aksi halde bazı PDF görüntüleyiciler özellikle kalın yazıda noktaları ve
    çengelleri harften kaymış çiziyor. İşlenen font önbelleğe yazılır, sonraki seferlerde doğrudan okunur.
    Bir hata olursa orijinal font yolu döner.
    """
    try:
        bilgi = os.stat(yol)
        ad = os.path.splitext(os.path.basename(yol))[0]
        hedef = os.path.join(_font_onbellek_klasoru(),
                             f"{ad}-{bilgi.st_size}-{int(bilgi.st_mtime)}-v{_FONT_ISLEME_SURUMU}.ttf")
        if os.path.exists(hedef):
            return hedef

        from fontTools import subset
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        from fontTools.ttLib import TTFont as FontToolsFont
        logging.getLogger("fontTools").setLevel(logging.ERROR)

        font = FontToolsFont(yol, fontNumber=0)  # .ttc dosyalarında ilk font
        secenekler = subset.Options()
        secenekler.hinting = False
        secenekler.layout_features = []
        secenekler.notdef_outline = True
        secenekler.name_IDs = ["*"]
        secenekler.name_languages = ["*"]
        alt_kume = subset.Subsetter(secenekler)
        alt_kume.populate(unicodes=[k for bas, son in _FONT_ARALIKLARI for k in range(bas, son + 1)])
        alt_kume.subset(font)

        glyf = font["glyf"]
        glif_seti = font.getGlyphSet()
        tek_parca = {}
        for glif_adi in font.getGlyphOrder():
            if glyf[glif_adi].isComposite():
                kayit = DecomposingRecordingPen(glif_seti)
                glif_seti[glif_adi].draw(kayit)
                kalem = TTGlyphPen(None)
                kayit.replay(kalem)
                tek_parca[glif_adi] = kalem.glyph()
        for glif_adi, glif in tek_parca.items():
            glyf[glif_adi] = glif

        os.makedirs(os.path.dirname(hedef), exist_ok=True)
        gecici = f"{hedef}.{os.getpid()}.tmp"
        font.save(gecici)
        os.replace(gecici, hedef)
        return hedef
    except Exception as e:
        print(f"Font işlenemedi, orijinali kullanılacak ({yol}): {e}")
        return yol


def fontlari_hazirla():
    """PDF fontlarını önceden işleyip önbelleğe alır (program açılışında arka planda çağrılır)."""
    for normal_yol, kalin_yol in _FONT_ADAYLARI:
        if os.path.exists(normal_yol) and os.path.exists(kalin_yol):
            _tek_parca_font(normal_yol)
            _tek_parca_font(kalin_yol)
            break
    for yol in _LOGO_FONT_ADAYLARI:
        if os.path.exists(yol):
            _tek_parca_font(yol)
            break


def turkce_fontlar():
    """Türkçe karakterleri doğru gösteren (normal, kalın) PDF font adlarını döndürür."""
    normal, kalin, _ = _fontlar()
    return normal, kalin


@lru_cache(maxsize=None)
def _fontlar():
    """(normal, kalın, logo) font adlarını döndürür. İlk PDF'te bir kez yüklenir."""
    normal, kalin = "Helvetica", "Helvetica-Bold"
    for normal_yol, kalin_yol in _FONT_ADAYLARI:
        if os.path.exists(normal_yol) and os.path.exists(kalin_yol):
            try:
                pdfmetrics.registerFont(TTFont("BelgeFont", _tek_parca_font(normal_yol)))
                pdfmetrics.registerFont(TTFont("BelgeFont-Bold", _tek_parca_font(kalin_yol)))
                normal, kalin = "BelgeFont", "BelgeFont-Bold"
                break
            except Exception as e:
                print(f"Font yüklenemedi ({normal_yol}): {e}")
    # Paragraflardaki <b> etiketi kalın fontu kullansın
    addMapping(normal, 0, 0, normal)
    addMapping(normal, 1, 0, kalin)
    addMapping(normal, 0, 1, normal)
    addMapping(normal, 1, 1, kalin)

    # "CLASSİC CAR" yazısı eski şablondaki gibi Cambria ile yazılır
    logo = kalin
    for yol in _LOGO_FONT_ADAYLARI:
        if os.path.exists(yol):
            try:
                pdfmetrics.registerFont(TTFont("BelgeLogo", _tek_parca_font(yol), subfontIndex=0))
                logo = "BelgeLogo"
                break
            except Exception as e:
                print(f"Logo fontu yüklenemedi ({yol}): {e}")
    return normal, kalin, logo


@lru_cache(maxsize=None)
def _stiller():
    normal, kalin, _ = _fontlar()

    def stil(ad, font=normal, boyut=8.5, satir=11, renk=colors.black, hiza=0, **ek):
        return ParagraphStyle(ad, fontName=font, fontSize=boyut, leading=satir, textColor=renk, alignment=hiza, **ek)

    return {
        "normal": stil("normal"),
        "etiket": stil("etiket", kalin, 7.5, 10, GRI_YAZI),
        "deger": stil("deger"),
        "deger_b": stil("deger_b", kalin, 9.5, 12),
        "kutu_baslik": stil("kutu_baslik", kalin, 8, 10, colors.white),
        "bolum": stil("bolum", kalin, 8.5, 11, KOYU),
        "th": stil("th", kalin, 7.5, 9.5, colors.white),
        "th_r": stil("th_r", kalin, 7.5, 9.5, colors.white, TA_RIGHT),
        "th_c": stil("th_c", kalin, 7.5, 9.5, colors.white, TA_CENTER),
        "td": stil("td", boyut=8, satir=10),
        "td_r": stil("td_r", boyut=8, satir=10, hiza=TA_RIGHT),
        "td_c": stil("td_c", boyut=8, satir=10, hiza=TA_CENTER),
        "td_alt": stil("td_alt", boyut=7, satir=9, renk=GRI_YAZI),
        "toplam_e": stil("toplam_e", boyut=8.5, satir=11, hiza=TA_RIGHT),
        "toplam_d": stil("toplam_d", boyut=8.5, satir=11, hiza=TA_RIGHT),
        "toplam_eb": stil("toplam_eb", kalin, 8.5, 11, hiza=TA_RIGHT),
        "toplam_db": stil("toplam_db", kalin, 8.5, 11, hiza=TA_RIGHT),
        "genel_e": stil("genel_e", kalin, 9.5, 12, colors.white, TA_RIGHT),
        "genel_d": stil("genel_d", kalin, 9.5, 12, colors.white, TA_RIGHT),
        "metin": stil("metin", boyut=8.5, satir=12),
        "kucuk": stil("kucuk", boyut=7.5, satir=10, renk=GRI_YAZI),
        "kutu_metin": stil("kutu_metin", boyut=8.5, satir=12, borderWidth=0.6, borderColor=CIZGI,
                           borderPadding=(5, 6, 6, 6), spaceBefore=5, spaceAfter=6),
        "imza_baslik": stil("imza_baslik", kalin, 8, 10, KOYU, TA_CENTER),
        "imza_alt": stil("imza_alt", boyut=7.5, satir=10, renk=GRI_YAZI, hiza=TA_CENTER),
    }


# ---------------------------------------------------------------- biçimlendirme

def _decimal(deger):
    try:
        return Decimal(str(deger if deger is not None else 0)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


def para_bicimi(tutar):
    """1234.5 -> '1.234,50 TL'"""
    metin = f"{_decimal(tutar):,.2f}"
    return metin.replace(",", "#").replace(".", ",").replace("#", ".") + " TL"


def tarih_bicimi(deger):
    """'2025-06-17' -> '17.06.2025'; tanınmayan değer olduğu gibi döner."""
    if not deger:
        return "-"
    metin = str(deger).strip()
    try:
        return datetime.datetime.strptime(metin[:10], "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return metin


def km_bicimi(deger):
    if deger in (None, ""):
        return "-"
    try:
        return f"{int(deger):,}".replace(",", ".") + " km"
    except (TypeError, ValueError):
        return str(deger)


def _oran_bicimi(oran):
    try:
        oran = float(oran or 0)
    except (TypeError, ValueError):
        return str(oran)
    return f"%{int(oran)}" if oran.is_integer() else f"%{oran:.2f}".replace(".", ",")


def _miktar_bicimi(miktar):
    try:
        miktar = float(miktar)
    except (TypeError, ValueError):
        return str(miktar)
    return str(int(miktar)) if miktar.is_integer() else f"{miktar:g}".replace(".", ",")


_BIRLER = ["", "Bir", "İki", "Üç", "Dört", "Beş", "Altı", "Yedi", "Sekiz", "Dokuz"]
_ONLAR = ["", "On", "Yirmi", "Otuz", "Kırk", "Elli", "Altmış", "Yetmiş", "Seksen", "Doksan"]
_BASAMAKLAR = ["", "Bin", "Milyon", "Milyar", "Trilyon"]


def _uc_basamak_yaziyla(sayi):
    yuz, on, bir = sayi // 100, (sayi // 10) % 10, sayi % 10
    parcalar = []
    if yuz:
        parcalar.append("Yüz" if yuz == 1 else f"{_BIRLER[yuz]} Yüz")
    if on:
        parcalar.append(_ONLAR[on])
    if bir:
        parcalar.append(_BIRLER[bir])
    return " ".join(parcalar)


def _sayi_yaziyla(sayi):
    if sayi == 0:
        return "Sıfır"
    gruplar = []
    basamak = 0
    while sayi > 0 and basamak < len(_BASAMAKLAR):
        grup = sayi % 1000
        if grup:
            # Türkçede "Bir Bin" denmez
            metin = "Bin" if basamak == 1 and grup == 1 else f"{_uc_basamak_yaziyla(grup)} {_BASAMAKLAR[basamak]}".strip()
            gruplar.append(metin)
        sayi //= 1000
        basamak += 1
    return " ".join(reversed(gruplar))


def tutar_yaziyla(tutar):
    """1234.5 -> 'Bin İki Yüz Otuz Dört Türk Lirası Elli Kuruş'"""
    deger = _decimal(tutar)
    negatif = deger < 0
    deger = abs(deger)
    lira = int(deger)
    kurus = int((deger - lira) * 100)
    metin = f"{_sayi_yaziyla(lira)} Türk Lirası"
    if kurus:
        metin += f" {_sayi_yaziyla(kurus)} Kuruş"
    return ("Eksi " if negatif else "") + metin


def _p(metin, stil):
    """Kullanıcı metnini güvenle Paragraph'a çevirir (özel karakterler kaçırılır, satır sonları korunur)."""
    metin = "" if metin is None else str(metin)
    if len(metin) > _MAX_HUCRE:
        metin = metin[:_MAX_HUCRE] + "…"
    return Paragraph(escape(metin).replace("\n", "<br/>"), stil)


def _bos_ise_tire(deger):
    return "-" if deger in (None, "") or str(deger).strip() == "" else deger


# ---------------------------------------------------------------- sayfa çerçevesi

class _SayfaliCanvas(rl_canvas.Canvas):
    """Toplam sayfa sayısını bilmek için sayfaları biriktirip kaydederken 'Sayfa X / Y' yazar."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sayfalar = []

    def showPage(self):
        self._sayfalar.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        toplam = len(self._sayfalar)
        for durum in self._sayfalar:
            self.__dict__.update(durum)
            normal, _, _ = _fontlar()
            self.setFont(normal, 7.5)
            self.setFillColor(GRI_YAZI)
            self.drawRightString(SAYFA_GENISLIK - KENAR, 10 * mm, f"Sayfa {self._pageNumber} / {toplam}")
            super().showPage()
        super().save()


def _ust_alt_bilgi_ciz(c, baslik, numara_etiket, numara, tarih):
    normal, kalin, logo = _fontlar()
    c.saveState()
    ust = SAYFA_YUKSEKLIK

    # Sol: firma
    c.setFillColor(LOGO_RENGI)
    c.setFont(logo, 24)
    c.drawString(KENAR, ust - 19 * mm, FIRMA["ad"])
    c.setFillColor(GRI_YAZI)
    c.setFont(normal, 7.5)
    y = ust - 24 * mm
    for satir in simpleSplit(FIRMA["adres"], normal, 7.5, 100 * mm) + [f"Tel: {FIRMA['telefon']}"]:
        c.drawString(KENAR, y, satir)
        y -= 3.3 * mm

    # Sağ: belge başlığı ve numarası
    sag = SAYFA_GENISLIK - KENAR
    c.setFillColor(KOYU)
    c.setFont(kalin, 17)
    c.drawRightString(sag, ust - 17 * mm, baslik)
    c.setFillColor(colors.black)
    c.setFont(kalin, 9)
    c.drawRightString(sag, ust - 23 * mm, f"{numara_etiket}: {numara}")
    c.setFont(normal, 8.5)
    c.drawRightString(sag, ust - 27.5 * mm, f"Tarih: {tarih}")

    c.setStrokeColor(KOYU)
    c.setLineWidth(1.4)
    c.line(KENAR, ust - 34 * mm, sag, ust - 34 * mm)

    # Alt bilgi (sayfa numarasını _SayfaliCanvas yazar)
    c.setStrokeColor(CIZGI)
    c.setLineWidth(0.5)
    c.line(KENAR, 14 * mm, sag, 14 * mm)
    c.setFillColor(GRI_YAZI)
    c.setFont(normal, 7)
    c.drawString(KENAR, 10 * mm, f"{FIRMA['ad']}  |  Tel: {FIRMA['telefon']}")
    c.restoreState()


def _belgeyi_yaz(dosya_yolu, baslik, numara_etiket, numara, tarih, akis):
    doc = BaseDocTemplate(
        dosya_yolu, pagesize=A4,
        leftMargin=KENAR, rightMargin=KENAR, topMargin=UST_BOSLUK, bottomMargin=ALT_BOSLUK,
        title=f"{baslik} {numara}", author=FIRMA["ad"], creator="OTO SERVİS PROGRAMI",
    )
    cerceve = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                    leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="icerik")

    def sayfa(c, _doc):
        _ust_alt_bilgi_ciz(c, baslik, numara_etiket, numara, tarih)

    doc.addPageTemplates([PageTemplate(id="sayfa", frames=[cerceve], onPage=sayfa)])
    doc.build(akis, canvasmaker=_SayfaliCanvas)


# ---------------------------------------------------------------- yapı taşları

def _bilgi_kutusu(baslik, satirlar, genislik, ek_alt_bosluk=0):
    """Başlıklı 'etiket: değer' kutusu. satirlar: [(etiket, deger), ...]"""
    st = _stiller()
    etiket_genislik = 25 * mm
    veri = [[_p(baslik, st["kutu_baslik"]), ""]]
    for etiket, deger in satirlar:
        deger_p = _p(_bos_ise_tire(deger), st["deger_b" if etiket == "Plaka" else "deger"])
        veri.append([_p(etiket, st["etiket"]), deger_p])
    tablo = Table(veri, colWidths=[etiket_genislik, genislik - etiket_genislik])
    tablo.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), KOYU),
        ("BOX", (0, 0), (-1, -1), 0.6, CIZGI),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, INCE_CIZGI),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("TOPPADDING", (0, 0), (-1, 0), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3.5),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 2.4 + ek_alt_bosluk),
    ]))
    return tablo


def _yan_yana(sol, sag, bosluk=6 * mm):
    genislik = (ICERIK_GENISLIK - bosluk) / 2
    tablo = Table([[sol, "", sag]], colWidths=[genislik, bosluk, genislik])
    tablo.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tablo


def _musteri_arac_kutulari(cari, arac, plaka, ilgili_kisi=None):
    genislik = (ICERIK_GENISLIK - 6 * mm) / 2
    musteri = [
        ("Ünvan", cari.get("cari_ad_unvan")),
        ("Cari Kodu", cari.get("cari_kodu")),
        ("Telefon", cari.get("cep_telefonu")),
        ("VKN / TCKN", cari.get("vergi_no") or cari.get("tc_kimlik_no")),
    ]
    if ilgili_kisi is not None:
        musteri.append(("İlgili Kişi", ilgili_kisi))
    marka_model = " ".join(str(x) for x in (arac.get("marka"), arac.get("model")) if x)
    arac_satirlari = [
        ("Plaka", plaka or arac.get("plaka")),
        ("Marka / Model", marka_model),
        ("Model Yılı", arac.get("model_yili")),
        ("Araç Tipi", arac.get("arac_tipi")),
        ("Şasi No", arac.get("sasi_no")),
        ("Motor No", arac.get("motor_no")),
    ]
    # İki kutu aynı yükseklikte görünsün: kısa olanın son satırına boşluk ekle
    sol = _bilgi_kutusu("MÜŞTERİ BİLGİLERİ", musteri, genislik)
    sag = _bilgi_kutusu("ARAÇ BİLGİLERİ", arac_satirlari, genislik)
    fark = sol.wrap(genislik, SAYFA_YUKSEKLIK)[1] - sag.wrap(genislik, SAYFA_YUKSEKLIK)[1]
    if fark > 0:
        sag = _bilgi_kutusu("ARAÇ BİLGİLERİ", arac_satirlari, genislik, fark)
    elif fark < 0:
        sol = _bilgi_kutusu("MÜŞTERİ BİLGİLERİ", musteri, genislik, -fark)
    return _yan_yana(sol, sag)


def _bilgi_seridi(ciftler, sutun_cifti=4):
    """Tam genişlikte, satır başına `sutun_cifti` adet 'etiket | değer' çifti."""
    st = _stiller()
    etiket_g = 23 * mm
    deger_g = (ICERIK_GENISLIK - sutun_cifti * etiket_g) / sutun_cifti
    satirlar = []
    for i in range(0, len(ciftler), sutun_cifti):
        grup = list(ciftler[i:i + sutun_cifti])
        grup += [("", "")] * (sutun_cifti - len(grup))
        satir = []
        for etiket, deger in grup:
            satir += [_p(etiket, st["etiket"]), _p(_bos_ise_tire(deger) if etiket else "", st["deger"])]
        satirlar.append(satir)
    tablo = Table(satirlar, colWidths=[etiket_g, deger_g] * sutun_cifti)
    komutlar = [
        ("BOX", (0, 0), (-1, -1), 0.6, CIZGI),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, INCE_CIZGI),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for kolon in range(0, 2 * sutun_cifti, 2):
        komutlar.append(("BACKGROUND", (kolon, 0), (kolon, -1), ACIK))
    tablo.setStyle(TableStyle(komutlar))
    return tablo


def _bolum_basligi(metin):
    tablo = Table([[_p(metin, _stiller()["bolum"])]], colWidths=[ICERIK_GENISLIK])
    tablo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACIK),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, KOYU),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tablo


def _kalem_tablosu(islemler):
    st = _stiller()
    # sıra, açıklama, miktar, birim fiyat, kdv %, kdv tutarı, tutar
    sabit = [8 * mm, None, 13 * mm, 25 * mm, 12 * mm, 23 * mm, 27 * mm]
    sabit[1] = ICERIK_GENISLIK - sum(g for g in sabit if g)
    veri = [[
        _p("#", st["th_c"]),
        _p("İşlem / Parça Açıklaması", st["th"]),
        _p("Miktar", st["th_c"]),
        _p("Birim Fiyat", st["th_r"]),
        _p("KDV", st["th_c"]),
        _p("KDV Tutarı", st["th_r"]),
        Paragraph("Tutar<br/>(KDV Hariç)", st["th_r"]),
    ]]
    for sira, islem in enumerate(islemler, 1):
        miktar = islem.get("miktar") or 1
        tutar = float(islem.get("islem_tutari") or 0)
        aciklama = [_p(islem.get("islem_aciklama"), st["td"])]
        if str(islem.get("aciklama") or "").strip():
            aciklama.append(_p(islem["aciklama"], st["td_alt"]))
        veri.append([
            _p(sira, st["td_c"]),
            aciklama,
            _p(_miktar_bicimi(miktar), st["td_c"]),
            _p(para_bicimi(tutar / float(miktar)), st["td_r"]),
            _p(_oran_bicimi(islem.get("kdv_orani")), st["td_c"]),
            _p(para_bicimi(islem.get("kdv_tutari")), st["td_r"]),
            _p(para_bicimi(tutar), st["td_r"]),
        ])
    komutlar = [
        ("BACKGROUND", (0, 0), (-1, 0), KOYU),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("VALIGN", (0, 1), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, CIZGI),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, INCE_CIZGI),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
    ]
    if not islemler:
        veri.append(["", _p("Kayıtlı işlem bulunmamaktadır.", st["td"]), "", "", "", "", ""])
        komutlar.append(("SPAN", (1, 1), (-1, 1)))
    tablo = Table(veri, colWidths=sabit, repeatRows=1)
    tablo.setStyle(TableStyle(komutlar))
    return tablo


def liste_tablosu(basliklar, satirlar, sutun_oranlari, genislik, sag_hizali=()):
    """
    Liste PDF'leri (araç, cari, ödeme) için tablo: sütuna sığmayan metin hücre içinde alt satıra kayar,
    başlık satırı her sayfada tekrarlanır. sutun_oranlari genişliği sütunlara orantılı dağıtır.
    """
    st = _stiller()
    toplam = float(sum(sutun_oranlari))
    veri = [[_p(b, st["th_r" if i in sag_hizali else "th"]) for i, b in enumerate(basliklar)]]
    for satir in satirlar:
        veri.append([_p(h, st["td_r" if i in sag_hizali else "td"]) for i, h in enumerate(satir)])
    tablo = Table(veri, colWidths=[genislik * o / toplam for o in sutun_oranlari], repeatRows=1)
    tablo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), KOYU),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.6, CIZGI),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, INCE_CIZGI),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
    ]))
    return tablo


def _toplamlari_hesapla(islemler):
    ara_toplam = sum(float(i.get("islem_tutari") or 0) for i in islemler)
    kdv_gruplari = {}
    for islem in islemler:
        oran = float(islem.get("kdv_orani") or 0)
        kdv_gruplari[oran] = kdv_gruplari.get(oran, 0.0) + float(islem.get("kdv_tutari") or 0)
    kdv_toplam = sum(kdv_gruplari.values())
    return ara_toplam, kdv_gruplari, kdv_toplam, ara_toplam + kdv_toplam


def _toplam_blogu(islemler, sol_icerik=None, ek_satirlar=()):
    """
    Sağda ara toplam / KDV dökümü / genel toplam, solda isteğe bağlı içerik (örn. tutar yazıyla).
    ek_satirlar: [(etiket, tutar, kalin_mi), ...] genel toplamın altına eklenir.
    """
    st = _stiller()
    ara_toplam, kdv_gruplari, kdv_toplam, genel_toplam = _toplamlari_hesapla(islemler)
    satirlar = [[_p("Ara Toplam (KDV Hariç)", st["toplam_e"]), _p(para_bicimi(ara_toplam), st["toplam_d"])]]
    kdv_satirlari = [(oran, tutar) for oran, tutar in sorted(kdv_gruplari.items()) if abs(tutar) >= 0.005]
    for oran, tutar in kdv_satirlari:
        satirlar.append([_p(f"KDV ({_oran_bicimi(oran)})", st["toplam_e"]), _p(para_bicimi(tutar), st["toplam_d"])])
    if not kdv_satirlari:
        satirlar.append([_p("KDV", st["toplam_e"]), _p(para_bicimi(0), st["toplam_d"])])
    genel_satir = len(satirlar)
    satirlar.append([_p("GENEL TOPLAM", st["genel_e"]), _p(para_bicimi(genel_toplam), st["genel_d"])])
    for etiket, tutar, kalin in ek_satirlar:
        satirlar.append([_p(etiket, st["toplam_eb" if kalin else "toplam_e"]),
                         _p(para_bicimi(tutar), st["toplam_db" if kalin else "toplam_d"])])

    sag = Table(satirlar, colWidths=[46 * mm, 34 * mm])
    sag.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, CIZGI),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, INCE_CIZGI),
        ("BACKGROUND", (0, genel_satir), (-1, genel_satir), KOYU),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    sol_genislik = ICERIK_GENISLIK - 80 * mm - 6 * mm
    dis = Table([[sol_icerik or "", "", sag]], colWidths=[sol_genislik, 6 * mm, 80 * mm])
    dis.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return dis, genel_toplam


def _yaziyla_kutusu(tutar, ek_metinler=()):
    st = _stiller()
    icerik = [Paragraph(f"<b>Yalnız:</b> {escape(tutar_yaziyla(tutar))}", st["metin"])]
    for metin in ek_metinler:
        icerik += [Spacer(1, 3), _p(metin, st["kucuk"])]
    return icerik


def _imza_kutusu(baslik, alt_yazi, genislik):
    st = _stiller()
    tablo = Table([[_p(baslik, st["imza_baslik"])], [""], [_p(alt_yazi, st["imza_alt"])]],
                  colWidths=[genislik], rowHeights=[None, 17 * mm, None])
    tablo.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, CIZGI),
        ("BACKGROUND", (0, 0), (-1, 0), ACIK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.3, CIZGI),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tablo


def _imza_alani(sol_baslik, sol_alt, sag_baslik, sag_alt):
    genislik = (ICERIK_GENISLIK - 6 * mm) / 2
    return _yan_yana(_imza_kutusu(sol_baslik, sol_alt, genislik), _imza_kutusu(sag_baslik, sag_alt, genislik))


class _Kutucuk(Flowable):
    """Elle işaretlenecek boş onay kutusu."""

    def __init__(self, boyut=3.2 * mm):
        super().__init__()
        self.width = self.height = boyut

    def draw(self):
        self.canv.setStrokeColor(GRI_YAZI)
        self.canv.setLineWidth(0.6)
        self.canv.rect(0, 0, self.width, self.height)


def _onay_kutulari(metinler):
    st = _stiller()
    kutu_g = 5 * mm
    metin_g = ICERIK_GENISLIK / len(metinler) - kutu_g
    satir = []
    for metin in metinler:
        satir += [_Kutucuk(), _p(metin, st["kucuk"])]
    tablo = Table([satir], colWidths=[kutu_g, metin_g] * len(metinler))
    tablo.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tablo


def _sayfa_bolunmeden(*parcalar):
    return KeepTogether([p for p in parcalar if p is not None])


# ---------------------------------------------------------------- belgeler

def is_emri_pdf(detaylar, dosya_yolu):
    """get_service_full_details() çıktısından iş emri PDF'i oluşturur."""
    st = _stiller()
    servis, cari, arac = detaylar["servis"], detaylar.get("cari") or {}, detaylar.get("arac") or {}
    islemler = detaylar.get("islemler") or []
    numara = f"{int(servis['id']):06d}"

    giris_km, cikis_km = servis.get("giris_km"), servis.get("cikis_km")
    yapilan_km = cikis_km - giris_km if giris_km is not None and cikis_km is not None and cikis_km >= giris_km else None
    akis = [
        _musteri_arac_kutulari(cari, arac, servis.get("plaka")),
        Spacer(1, 5 * mm),
        _bilgi_seridi([
            ("İş Emri No", numara),
            ("Açılış Tarihi", tarih_bicimi(servis.get("servis_tarihi"))),
            ("Durum", servis.get("servis_durumu")),
            ("Kapanış Tarihi", tarih_bicimi(servis.get("servis_kapanis_tarihi"))),
            ("Aracı Getiren", servis.get("arac_getiren_kisi")),
            ("Giriş KM", km_bicimi(giris_km)),
            ("Çıkış KM", km_bicimi(cikis_km)),
            ("Yapılan KM", km_bicimi(yapilan_km)),
        ]),
        Spacer(1, 5 * mm),
        _bolum_basligi("MÜŞTERİ TALEPLERİ / ŞİKAYETLER"),
        _p(_bos_ise_tire(servis.get("aciklama")), st["kutu_metin"]),
        Spacer(1, 3 * mm),
        _bolum_basligi("YAPILAN İŞLEMLER VE KULLANILAN PARÇALAR"),
        Spacer(1, 2 * mm),
        _kalem_tablosu(islemler),
        Spacer(1, 4 * mm),
    ]
    toplam, _ = _toplam_blogu(islemler)
    akis.append(toplam)
    akis.append(Spacer(1, 6 * mm))
    akis.append(_sayfa_bolunmeden(
        _onay_kutulari([
            "Çıkan parçalar müşteriye teslim edilecektir.",
            "Bu araçta orijinal yedek parça kullanılmıştır.",
            "Bu araçta muadil yedek parça kullanılmıştır.",
        ]),
        Spacer(1, 5 * mm),
        _imza_alani("MÜŞTERİ", "Aracı Teslim Eden — İsim / İmza", "SERVİS DANIŞMANI", "İsim / İmza"),
        Spacer(1, 3 * mm),
        _yan_yana(
            _p(f"Onarım Bitiş Tarihi: {tarih_bicimi(servis.get('servis_kapanis_tarihi')) if servis.get('servis_kapanis_tarihi') else '...... / ...... / ............'}", st["kucuk"]),
            _p("Araç Teslim Tarihi: ...... / ...... / ............", st["kucuk"]),
        ),
    ))
    _belgeyi_yaz(dosya_yolu, "İŞ EMRİ", "İş Emri No", numara, tarih_bicimi(servis.get("servis_tarihi")), akis)


def fatura_pdf(detaylar, dosya_yolu, odenen_tutar=0.0):
    """get_service_full_details() çıktısından ödeme durumunu da gösteren fatura PDF'i oluşturur."""
    servis, cari, arac = detaylar["servis"], detaylar.get("cari") or {}, detaylar.get("arac") or {}
    islemler = detaylar.get("islemler") or []
    numara = f"{int(servis['id']):06d}"
    fatura_tarihi = tarih_bicimi(servis.get("servis_kapanis_tarihi") or datetime.date.today().isoformat())

    akis = [
        _musteri_arac_kutulari(cari, arac, servis.get("plaka")),
        Spacer(1, 5 * mm),
        _bilgi_seridi([
            ("Fatura No", numara),
            ("Fatura Tarihi", fatura_tarihi),
            ("İş Emri No", numara),
            ("Servis Tarihi", tarih_bicimi(servis.get("servis_tarihi"))),
            ("Giriş KM", km_bicimi(servis.get("giris_km"))),
            ("Çıkış KM", km_bicimi(servis.get("cikis_km"))),
        ], sutun_cifti=3),
        Spacer(1, 5 * mm),
        _bolum_basligi("HİZMET VE PARÇA DÖKÜMÜ"),
        Spacer(1, 2 * mm),
        _kalem_tablosu(islemler),
        Spacer(1, 4 * mm),
    ]
    _, _, _, genel_toplam = _toplamlari_hesapla(islemler)
    odenen = float(odenen_tutar or 0)
    toplam, _ = _toplam_blogu(
        islemler,
        sol_icerik=_yaziyla_kutusu(genel_toplam),
        ek_satirlar=[("Ödenen", odenen, False), ("Kalan Bakiye", max(genel_toplam - odenen, 0.0), True)],
    )
    akis.append(toplam)
    akis.append(Spacer(1, 8 * mm))
    akis.append(_sayfa_bolunmeden(
        _imza_alani("DÜZENLEYEN", FIRMA["ad"], "TESLİM ALAN", "İsim / İmza"),
    ))
    _belgeyi_yaz(dosya_yolu, "FATURA", "Fatura No", numara, fatura_tarihi, akis)


def teklif_pdf(detaylar, dosya_yolu):
    """get_teklif_details() çıktısından teklif PDF'i oluşturur."""
    st = _stiller()
    teklif, cari, arac = detaylar["teklif"], detaylar.get("cari") or {}, detaylar.get("arac") or {}
    islemler = detaylar.get("islemler") or []
    cari = dict(cari, cari_kodu=teklif.get("cari_kodu"))
    gecerlilik = tarih_bicimi(teklif.get("gecerlilik_tarihi"))
    vade = teklif.get("odeme_vade_gun")

    akis = [
        _musteri_arac_kutulari(cari, arac, teklif.get("plaka"), ilgili_kisi=teklif.get("teklif_alan")),
        Spacer(1, 5 * mm),
        _bilgi_seridi([
            ("Teklif No", teklif.get("teklif_no")),
            ("Teklif Tarihi", tarih_bicimi(teklif.get("teklif_tarihi"))),
            ("Geçerlilik", gecerlilik),
            ("Ödeme Şekli", teklif.get("odeme_sekli")),
            ("Vade", f"{vade} gün" if vade not in (None, "", 0) else None),
            ("Teklif Veren", teklif.get("teklif_veren_personel")),
        ], sutun_cifti=3),
        Spacer(1, 5 * mm),
        _p(f"Sayın {cari.get('cari_ad_unvan') or 'Müşterimiz'}, aracınız için bakım / onarım / yedek parça "
           "tedarikine yönelik olarak hazırlanan teklifimiz aşağıda bilgilerinize sunulmuştur.", st["metin"]),
        Spacer(1, 4 * mm),
        _kalem_tablosu(islemler),
        Spacer(1, 4 * mm),
    ]
    _, _, _, genel_toplam = _toplamlari_hesapla(islemler)
    toplam, _ = _toplam_blogu(
        islemler,
        sol_icerik=_yaziyla_kutusu(genel_toplam, [f"Bu teklif {gecerlilik} tarihine kadar geçerlidir."]),
    )
    akis.append(toplam)
    if str(teklif.get("aciklama") or "").strip():
        akis += [Spacer(1, 5 * mm), _bolum_basligi("NOTLAR"), _p(teklif["aciklama"], st["kutu_metin"])]
    akis.append(Spacer(1, 8 * mm))
    veren_alt = FIRMA["ad"] + (f" — {teklif['teklif_veren_personel']}" if teklif.get("teklif_veren_personel") else "")
    akis.append(_sayfa_bolunmeden(
        _imza_alani("TEKLİFİ VEREN", veren_alt, "TEKLİFİ ONAYLAYAN", "İsim / İmza / Kaşe"),
    ))
    _belgeyi_yaz(dosya_yolu, "TEKLİF FORMU", "Teklif No", teklif.get("teklif_no"),
                 tarih_bicimi(teklif.get("teklif_tarihi")), akis)
