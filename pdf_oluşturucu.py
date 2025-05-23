from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# DejaVuSans fontunu kaydet
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans.ttf'))

def teklif_pdf_olustur(dosya_adi="teklif_formu.pdf"):
    c = canvas.Canvas(dosya_adi, pagesize=A4)
    width, height = A4

    # LOGO EKLEME (sol üst köşe)
    logo_path = "logo.png"
    logo_width = 40 * mm
    logo_height = 25 * mm
    c.drawImage(logo_path, 20 * mm, height - 40 * mm, width=logo_width, height=logo_height, mask='auto')

    # Firma Bilgileri
    c.setFont("DejaVuSans", 11)
    c.drawString(65 * mm, height - 25 * mm, "Classic Car")
    c.setFont("DejaVuSans", 9)
    c.drawString(65 * mm, height - 32 * mm, "Adana/sarıçam osman gazi mahallesi 2037 sokak")
    c.drawString(65 * mm, height - 38 * mm, "0545 468 58 37")

    # Başlık
    c.setFont("DejaVuSans-Bold", 15)
    c.drawCentredString(width / 2, height - 55 * mm, "TEKLİF FORMU")

    # Sağ üstte tarih ve teklif no
    c.setFont("DejaVuSans", 9)
    c.drawString(width - 70 * mm, height - 40 * mm, "Teklif Tarihi :")
    c.drawString(width - 70 * mm, height - 47 * mm, "Teklif Numarası :")

    # Cari Bilgileri (sol)
    c.setFont("DejaVuSans-Bold", 9)
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
    c.setFont("DejaVuSans-Bold", 8)
    tablo_basliklari = ["S/N", "Ürün Kodu", "Ürün / Hizmet Cinsi", "Miktarı", "Birimi", "Birim Fiyat", "İsk.%", "Toplam"]
    xler = [22, 38, 60, 110, 125, 140, 160, 175]
    for i, baslik in enumerate(tablo_basliklari):
        c.drawString(xler[i] * mm, height - 115 * mm, baslik)

    # Notlar
    c.setFont("DejaVuSans-Bold", 9)
    c.setFillColor(colors.red)
    c.drawString(22 * mm, 60 * mm, "Notlar :")
    c.setFillColor(colors.black)

    # Sağ alt toplamlar
    c.setFont("DejaVuSans", 9)
    toplamlar = ["Ara Toplam:", "İndirimli Tutar:", "İndirimli Ara Toplam:", "KDV Tutarı:", "GENEL TOPLAM:"]
    for i, t in enumerate(toplamlar):
        c.drawRightString(width - 25 * mm, 90 * mm - i * 6 * mm, t)

    # Alt imza kutuları
    c.setFont("DejaVuSans-Bold", 9)
    c.setDash(3, 2)  # Kesikli çizgi ayarı
    c.rect(20 * mm, 20 * mm, 85 * mm, 20 * mm)
    c.rect(105 * mm, 20 * mm, 85 * mm, 20 * mm)
    c.setDash()  # Çizgiyi normale döndür
    c.drawCentredString(62.5 * mm, 37 * mm, "TEKLİFİ VEREN")
    c.drawCentredString(147.5 * mm, 37 * mm, "TEKLİFİ ONAYLAYAN")
    c.setFont("DejaVuSans", 10)
    c.drawCentredString(62.5 * mm, 30 * mm, "Classic Car")
    c.drawCentredString(147.5 * mm, 30 * mm, "İSİM/İMZA/KAŞE")

    # Alt mavi bar
    c.setFillColor(colors.HexColor("#3399ff"))
    c.rect(20 * mm, 10 * mm, width - 40 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("DejaVuSans-Bold", 8)
    c.drawCentredString(width / 2, 13 * mm, "DENEME FİRMASI\nBURAYA ADRESİNİZİ YAZINIZ\nTel: 0224 000 00 00  E-Mail:")

    c.save()

if __name__ == "__main__":
    teklif_pdf_olustur()