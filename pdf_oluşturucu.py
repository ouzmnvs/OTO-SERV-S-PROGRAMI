# encoding:utf-8
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from io import BytesIO
import os
import sys
import locale

def turkce_karakter_duzelt(text):
    """Türkçe karakterleri UTF-8 karakterlere dönüştürür"""
    if not isinstance(text, str):
        return str(text)
    
    tr_chars = {
        'ç': '\xc3\xa7', 'Ç': '\xc3\x87',  # LATIN SMALL/CAPITAL LETTER C WITH CEDILLA
        'ğ': '\xc4\x9f', 'Ğ': '\xc4\x9e',  # LATIN SMALL/CAPITAL LETTER G WITH BREVE
        'ı': '\xc4\xb1', 'İ': '\xc4\xb0',  # LATIN SMALL/CAPITAL LETTER I WITH DOT ABOVE
        'ö': '\xc3\xb6', 'Ö': '\xc3\x96',  # LATIN SMALL/CAPITAL LETTER O WITH DIAERESIS
        'ş': '\xc5\x9f', 'Ş': '\xc5\x9e',  # LATIN SMALL/CAPITAL LETTER S WITH CEDILLA
        'ü': '\xc3\xbc', 'Ü': '\xc3\x9c'   # LATIN SMALL/CAPITAL LETTER U WITH DIAERESIS
    }
    
    for tr_char, utf8_char in tr_chars.items():
        text = text.replace(tr_char, utf8_char)
    
    return text

# Türkçe karakter desteği için locale ayarı
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except:
        pass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Font kayıt işlemi
try:
    # Her iki fontu da kaydet
    font_path_normal = resource_path('arial-unicode-ms.ttf')
    font_path_bold = resource_path('arial-unicode-ms-bold.ttf')
    
    if os.path.exists(font_path_normal) and os.path.exists(font_path_bold):
        pdfmetrics.registerFont(TTFont('ArialUnicode', font_path_normal))
        pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', font_path_bold))
        FONT_NAME = 'ArialUnicode'
        FONT_NAME_BOLD = 'ArialUnicode-Bold'
    else:
        print("Warning: Font dosyaları bulunamadı, varsayılan fontlar kullanılacak")
        FONT_NAME = 'Times-Roman'
        FONT_NAME_BOLD = 'Times-Bold'
except Exception as e:
    print(f"Warning: Font yükleme hatası: {e}")
    FONT_NAME = 'Times-Roman'
    FONT_NAME_BOLD = 'Times-Bold'

def teklif_pdf_olustur(dosya_adi="teklif_formu.pdf"):
    # PDF oluşturma işlemi için encoding ayarı
    c = canvas.Canvas(dosya_adi, pagesize=A4)
    c.setTitle("Teklif Formu")
    c.setAuthor("Classic Car")
    c.setCreator("PDF Oluşturucu")
    
    # Türkçe karakter desteği için encoding ayarı
    c._doc.Catalog.OpenAction = None
    c._doc.Catalog.Lang = 'tr-TR'
    width, height = A4

    # LOGO EKLEME (sol üst köşe)
    logo_path = "logo.png"
    logo_width = 40 * mm
    logo_height = 25 * mm
    c.drawImage(logo_path, 20 * mm, height - 40 * mm, width=logo_width, height=logo_height, mask='auto')

    # Firma Bilgileri
    c.setFont(FONT_NAME, 11)
    c.drawString(65 * mm, height - 25 * mm, "Classic Car")
    c.setFont(FONT_NAME, 9)
    c.drawString(65 * mm, height - 32 * mm, "Adana/sarıçam osman gazi mahallesi 2037 sokak")
    c.drawString(65 * mm, height - 38 * mm, "0545 468 58 37")

    # Başlık
    c.setFont(FONT_NAME_BOLD, 15)
    c.drawCentredString(width / 2, height - 55 * mm, "TEKLİF FORMU")

    # Sağ üstte tarih ve teklif no
    c.setFont(FONT_NAME, 9)
    c.drawString(width - 70 * mm, height - 40 * mm, "Teklif Tarihi :")
    c.drawString(width - 70 * mm, height - 47 * mm, "Teklif Numarası :")

    # Cari Bilgileri (sol)
    c.setFont(FONT_NAME_BOLD, 9)
    c.drawString(25 * mm, height - 65 * mm, "Cari")
    c.drawString(25 * mm, height - 72 * mm, "Adres")
    c.drawString(25 * mm, height - 79 * mm, "İlgili Kişi")
    c.drawString(25 * mm, height - 86 * mm, "Plaka")
    c.drawString(25 * mm, height - 93 * mm, "Cep No")
    c.drawString(25 * mm, height - 100 * mm, "EMail")
    c.drawString(25 * mm, height - 107 * mm, "KONU")

    # Tablo Başlığı
    c.setFillColor(colors.HexColor("#dbe8fa"))
    c.rect(20 * mm, height - 120 * mm, width - 40 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONT_NAME_BOLD, 8)
    tablo_basliklari = ["S/N", "Ürün Kodu", "Ürün / Hizmet Cinsi", "Miktarı", "Birimi", "Birim Fiyat", "İsk.%", "Toplam"]
    xler = [22, 38, 60, 110, 125, 140, 160, 175]
    for i, baslik in enumerate(tablo_basliklari):
        c.drawString(xler[i] * mm, height - 115 * mm, baslik)

    # Notlar
    c.setFont(FONT_NAME_BOLD, 9)
    c.setFillColor(colors.red)
    c.drawString(22 * mm, 60 * mm, "Notlar :")
    c.setFillColor(colors.black)

    # Sağ alt toplamlar
    c.setFont(FONT_NAME, 9)
    toplamlar = ["Ara Toplam:", "İndirimli Tutar:", "İndirimli Ara Toplam:", "KDV Tutarı:", "GENEL TOPLAM:"]
    for i, t in enumerate(toplamlar):
        c.drawRightString(width - 25 * mm, 90 * mm - i * 6 * mm, t)

    # Alt imza kutuları
    c.setFont(FONT_NAME_BOLD, 9)
    c.setDash(3, 2)  # Kesikli çizgi ayarı
    c.rect(20 * mm, 20 * mm, 85 * mm, 20 * mm)
    c.rect(105 * mm, 20 * mm, 85 * mm, 20 * mm)
    c.setDash()  # Çizgiyi normale döndür
    c.drawCentredString(62.5 * mm, 37 * mm, "TEKLİFİ VEREN")
    c.drawCentredString(147.5 * mm, 37 * mm, "TEKLİFİ ONAYLAYAN")
    c.setFont(FONT_NAME, 10)
    c.drawCentredString(62.5 * mm, 30 * mm, "Classic Car")
    c.drawCentredString(147.5 * mm, 30 * mm, "İSİM/İMZA/KAŞE")

    # Alt mavi bar
    c.setFillColor(colors.HexColor("#3399ff"))
    c.rect(20 * mm, 10 * mm, width - 40 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_NAME_BOLD, 8)
    c.drawCentredString(width / 2, 13 * mm, "DENEME FİRMASI\nBURAYA ADRESİNİZİ YAZINIZ\nTel: 0224 000 00 00  E-Mail:")

    c.save()

def mevcut_pdf_duzenle(kaynak_pdf, hedef_pdf, eklemeler, font_size=8):
    doc = fitz.open(resource_path(kaynak_pdf))
    
    # Her iki font dosyasının yolunu al
    font_path_normal = resource_path('arial-unicode-ms.ttf')
    font_path_bold = resource_path('arial-unicode-ms-bold.ttf')
    
    if not os.path.exists(font_path_normal) or not os.path.exists(font_path_bold):
        print("Font dosyaları bulunamadı, varsayılan fontlar kullanılacak")
        font_path_normal = None
        font_path_bold = None

    for page in doc:
        if 'text' in eklemeler:
            for item in eklemeler['text']:
                if len(item) == 4:
                    x, y, text, font_size = item
                    x_point = x * 2.83465
                    y_point = page.rect.height - (y * 2.83465)

                    # İşlem satırları için normal font, diğerleri için bold font kullan
                    is_islem = False
                    if 155 <= y <= 155 - (len(eklemeler['text']) * 3):  # İşlem satırları aralığı
                        is_islem = True

                    page.insert_text(
                        (x_point, y_point),
                        text,
                        fontsize=font_size,
                        fontname="ArialUnicode" if is_islem else "ArialUnicode-Bold",
                        fontfile=font_path_normal if is_islem else font_path_bold,
                        color=(0, 0, 0)
                    )
                else:
                    x, y, text = item
                    x_point = x * 2.83465
                    y_point = page.rect.height - (y * 2.83465)

                    # İşlem satırları için normal font, diğerleri için bold font kullan
                    is_islem = False
                    if 155 <= y <= 155 - (len(eklemeler['text']) * 3):  # İşlem satırları aralığı
                        is_islem = True

                    page.insert_text(
                        (x_point, y_point),
                        text,
                        fontsize=font_size,
                        fontname="ArialUnicode" if is_islem else "ArialUnicode-Bold",
                        fontfile=font_path_normal if is_islem else font_path_bold,
                        color=(0, 0, 0)
                    )
        if 'image' in eklemeler:
            for x, y, img_path, width, height in eklemeler['image']:
                x_point = x * 2.83465
                y_point = page.rect.height - (y * 2.83465)
                width_point = width * 2.83465
                height_point = height * 2.83465
                img_rect = fitz.Rect(x_point, y_point, x_point + width_point, y_point + height_point)
                page.insert_image(img_rect, filename=img_path)
                
    doc.save(hedef_pdf)
    doc.close()
