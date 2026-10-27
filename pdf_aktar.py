"""PDF AKTAR butonlarının ortak akışı: belge türünü sor, kayıt yerini sor, oluştur, istenirse aç."""
import os
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

_son_klasor = ""  # Oturum boyunca son kaydedilen klasör hatırlanır


def _guvenli_dosya_adi(ad):
    return re.sub(r'[\\/:*?"<>|]+', "_", ad).strip()


def _kayit_yolu_sor(parent, varsayilan_ad):
    global _son_klasor
    yol, _ = QFileDialog.getSaveFileName(
        parent,
        "PDF Dosyasını Kaydet",
        os.path.join(_son_klasor, _guvenli_dosya_adi(varsayilan_ad)),
        "PDF Dosyaları (*.pdf)"
    )
    if not yol:
        return None
    if not yol.lower().endswith(".pdf"):
        yol += ".pdf"
    _son_klasor = os.path.dirname(yol)
    return yol


def _olustur_ve_bildir(parent, yol, olustur):
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        olustur(yol)
    except PermissionError:
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(parent, "Hata",
                             f"PDF kaydedilemedi:\n{yol}\n\nDosya başka bir programda açık olabilir. Kapatıp tekrar deneyin.")
        return
    except Exception as e:
        QApplication.restoreOverrideCursor()
        QMessageBox.critical(parent, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")
        return
    QApplication.restoreOverrideCursor()

    kutu = QMessageBox(parent)
    kutu.setIcon(QMessageBox.Information)
    kutu.setWindowTitle("Başarılı")
    kutu.setText(f"PDF dosyası oluşturuldu:\n{yol}")
    btn_ac = kutu.addButton("PDF'i Aç", QMessageBox.AcceptRole)
    kutu.addButton("Tamam", QMessageBox.RejectRole)
    kutu.exec_()
    if kutu.clickedButton() is btn_ac:
        try:
            os.startfile(yol)
        except OSError as e:
            QMessageBox.warning(parent, "Uyarı", f"PDF açılamadı:\n{str(e)}")


def belge_turu_sor(parent, varsayilan="is_emri"):
    """'is_emri', 'fatura' veya iptal edilirse None döndürür."""
    kutu = QMessageBox(parent)
    kutu.setIcon(QMessageBox.Question)
    kutu.setWindowTitle("PDF Aktar")
    kutu.setText("Hangi belgeyi oluşturmak istiyorsunuz?")
    btn_is_emri = kutu.addButton("İş Emri", QMessageBox.AcceptRole)
    btn_fatura = kutu.addButton("Fatura", QMessageBox.AcceptRole)
    kutu.addButton("İptal", QMessageBox.RejectRole)
    kutu.setDefaultButton(btn_fatura if varsayilan == "fatura" else btn_is_emri)
    kutu.exec_()
    if kutu.clickedButton() is btn_is_emri:
        return "is_emri"
    if kutu.clickedButton() is btn_fatura:
        return "fatura"
    return None


def servis_pdf_aktar(parent, servis_id, varsayilan="is_emri"):
    """Seçili servis için iş emri veya fatura PDF'i oluşturur."""
    from database_progress import get_service_full_details, get_servis_odenen_tutar

    tur = belge_turu_sor(parent, varsayilan)
    if not tur:
        return

    detaylar = get_service_full_details(int(servis_id))
    if not detaylar:
        QMessageBox.warning(parent, "Uyarı", "Servis detayları bulunamadı!")
        return

    servis = detaylar["servis"]
    is_emri_no = f"{int(servis['id']):06d}"
    on_ek = "is_emri" if tur == "is_emri" else "fatura"
    yol = _kayit_yolu_sor(parent, f"{on_ek}_{is_emri_no}_{servis['plaka']}_{servis['servis_tarihi']}.pdf")
    if not yol:
        return

    import pdf_belgeler
    if tur == "is_emri":
        _olustur_ve_bildir(parent, yol, lambda p: pdf_belgeler.is_emri_pdf(detaylar, p))
    else:
        odenen = get_servis_odenen_tutar(servis["id"])
        _olustur_ve_bildir(parent, yol, lambda p: pdf_belgeler.fatura_pdf(detaylar, p, odenen))


def teklif_pdf_aktar(parent, teklif_no):
    """Teklif numarasına göre teklif PDF'i oluşturur."""
    from database_progress import get_teklif_details

    detaylar = get_teklif_details(teklif_no)
    if not detaylar:
        QMessageBox.warning(parent, "Uyarı", "Teklif detayları bulunamadı!")
        return

    teklif = detaylar["teklif"]
    yol = _kayit_yolu_sor(parent, f"teklif_{teklif['teklif_no']}_{teklif['teklif_tarihi']}.pdf")
    if not yol:
        return

    import pdf_belgeler
    _olustur_ve_bildir(parent, yol, lambda p: pdf_belgeler.teklif_pdf(detaylar, p))
