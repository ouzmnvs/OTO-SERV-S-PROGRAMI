import fitz  # PyMuPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# DejaVuSans.ttf dosyasının yolu (scriptle aynı dizinde olduğunu varsayıyorum)
FONT_PATH = "DejaVuSans.ttf"
FONT_NAME = "DejaVuSans"

# PyMuPDF'ye DejaVuSans fontunu gömme (embedding) için ilk adım:
# fitz.Font() kullanacağız.

def pdf_ustu_yaz(input_pdf, output_pdf, yazilar):
    """
    Var olan PDF üzerine yazı ekler.

    Args:
        input_pdf (str): Kaynak PDF dosyası
        output_pdf (str): Kaydedilecek yeni PDF dosyası
        yazilar (list of dict): Üstüne yazılacak yazılar, format:
            [
                {"sayfa": 0, "x": 50, "y": 100, "text": "Merhaba Dünya", "font_size": 12},
                ...
            ]
            (x,y) koordinatları point cinsindendir (1 point = 1/72 inch)
    """
    doc = fitz.open(input_pdf)

    # DejaVuSans fontunu PyMuPDF'ye göm
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"{FONT_PATH} bulunamadı, aynı klasörde olduğundan emin olun.")
    font = fitz.Font(fontfile=FONT_PATH)

    for yazi in yazilar:
        sayfa_no = yazi.get("sayfa", 0)
        x = yazi.get("x", 50)
        y = yazi.get("y", 100)
        text = yazi.get("text", "")
        font_size = yazi.get("font_size", 12)

        sayfa = doc[sayfa_no]

        # Yazı ekle (DejaVuSans fontu ile)
        sayfa.insert_text(
            point=(x, y),
            text=text,
            fontname=FONT_NAME,
            fontsize=font_size,
            fontfile=FONT_PATH,
            color=(0, 0, 0)  # Siyah renk
        )

    doc.save(output_pdf)
    doc.close()

if __name__ == "__main__":
    # Test için örnek
    input_pdf = "teklif.pdf"    # Üzerine yazılacak dosya
    output_pdf = "teklif_yeni.pdf"

    yazilar = [
        {"sayfa": 0, "x": 50, "y": 50, "text": "Merhaba Şişli, Çalışıyor!", "font_size": 14},
        {"sayfa": 0, "x": 50, "y": 70, "text": "İkinci satır örneği: ğ, ü, ş, ö, ç, ı", "font_size": 12},
    ]

    pdf_ustu_yaz(input_pdf, output_pdf, yazilar)
