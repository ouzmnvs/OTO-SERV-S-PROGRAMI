from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from qtawesome import icon

class ServisKayitlariForm(QDialog):
    def __init__(self, cari_ad, plaka, arac_tipi, model_yili, marka, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Servis Kayıtları")
        self.setFixedSize(700, 500)
        self.cari_ad = cari_ad
        self.plaka = plaka
        self.arac_tipi = arac_tipi
        self.model_yili = model_yili
        self.marka = marka
        self.model = model
        self.init_ui()

    def init_ui(self):
        ana_layout = QVBoxLayout()

        # Üst butonlar
        buton_layout = QHBoxLayout()
        btn_detay = QPushButton(icon('fa5s.file-alt', color='#1976d2'), "DETAY GÖRÜNTÜLE")
        btn_detay.clicked.connect(self.detay_goruntule)
        btn_kapat = QPushButton(icon('fa5s.times', color='#b71c1c'), "SAYFAYI KAPAT")
        btn_kapat.clicked.connect(self.close)
        buton_layout.addWidget(btn_detay)
        buton_layout.addStretch()
        buton_layout.addWidget(btn_kapat)
        ana_layout.addLayout(buton_layout)

        # Araç Bilgileri
        arac_group = QGroupBox("Araç Bilgileri")
        arac_layout = QHBoxLayout()
        arac_layout.addLayout(self._label_value("Cari Adı", self.cari_ad))
        arac_layout.addLayout(self._label_value("Araç Tipi", self.arac_tipi))
        arac_layout.addLayout(self._label_value("Marka", self.marka))
        arac_layout.addLayout(self._label_value("Plaka", self.plaka))
        arac_layout.addLayout(self._label_value("Model Yılı", str(self.model_yili)))
        arac_layout.addLayout(self._label_value("Model", self.model))
        arac_group.setLayout(arac_layout)
        ana_layout.addWidget(arac_group)

        # Servis Kayıtları Tablosu
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Tarih", "Tutar", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        ana_layout.addWidget(self.table)

        # Alt bilgi
        self.lbl_alt = QLabel("")
        self.lbl_alt.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        ana_layout.addWidget(self.lbl_alt)

        self.setLayout(ana_layout)
        self.load_servis_kayitlari()

    def _label_value(self, label, value):
        layout = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("font-weight: bold;")
        val = QLabel(str(value))
        val.setStyleSheet("background: #f5f5f5; border: 1px solid #ccc; border-radius: 4px; padding: 4px 8px;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        return layout

    def load_servis_kayitlari(self):
        # Veritabanından servis kayıtlarını çek
        from database_progress import load_servis_kayitlari_by_plaka
        kayitlar = load_servis_kayitlari_by_plaka(self.plaka)
        self.table.setRowCount(len(kayitlar))
        toplam_tutar = 0
        for row, (tarih, tutar, durum) in enumerate(kayitlar):
            self.table.setItem(row, 0, QTableWidgetItem(tarih))
            self.table.setItem(row, 1, QTableWidgetItem(f"{tutar:,.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(durum))
            toplam_tutar += tutar
        self.lbl_alt.setText(f"{len(kayitlar)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:,.2f} TL")

    def detay_goruntule(self):
        from PyQt5.QtWidgets import QMessageBox, QFileDialog
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_tarihi = self.table.item(selected_row, 0).text()
        from database_progress import load_service_details, load_service_operations, load_cari_details, load_car_details
        import sqlite3
        conn = sqlite3.connect("oto_servis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM SERVİSLER WHERE plaka=? AND servis_tarihi=?", (self.plaka, servis_tarihi))
        row = cursor.fetchone()
        conn.close()
        if not row:
            QMessageBox.warning(self, "Uyarı", "Servis kaydı bulunamadı!")
            return
        servis_id = row[0]

        servis_bilgi = load_service_details(servis_id)
        islem_listesi = load_service_operations(servis_id)
        cari_bilgi = load_cari_details(servis_bilgi.get("cari_kodu", "")) if servis_bilgi else {}
        arac_bilgi = load_car_details(self.plaka)

        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", f"servis_{servis_id}.pdf", "PDF Files (*.pdf)")
        if not dosya_yolu:
            return

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        # Türkçe karakter desteği için DejaVuSans fontunu ekle
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        if not os.path.exists(font_path):
            from reportlab.rl_config import TTFSearchPath
            for p in TTFSearchPath:
                test_path = os.path.join(p, "DejaVuSans.ttf")
                if os.path.exists(test_path):
                    font_path = test_path
                    break
        pdfmetrics.registerFont(TTFont("DejaVu", font_path))

        c = canvas.Canvas(dosya_yolu, pagesize=A4)
        width, height = A4
        y = height - 25 * mm

        # Başlık
        c.setFont("DejaVu", 18)
        c.drawCentredString(width / 2, y, "SERVİS DETAY RAPORU")
        y -= 15 * mm

        # --- Bilgi Kutusu ---
        c.setFont("DejaVu", 10)
        kutu_yukseklik = 32 * mm
        c.setFillColor(colors.lightgrey)
        c.rect(15*mm, y - kutu_yukseklik + 5*mm, width-30*mm, kutu_yukseklik, fill=1, stroke=0)
        c.setFillColor(colors.black)
        satir_aralik = 7 * mm

        def yazdir_bilgi(x, y, label, value):
            c.drawString(x, y, f"{label}: {value}")

        # Cari Bilgileri
        y_kutu = y + kutu_yukseklik - 10*mm
        yazdir_bilgi(20*mm, y_kutu, "Cari Bilgileri", "")
        yazdir_bilgi(50*mm, y_kutu, "Cari Kodu", servis_bilgi.get('cari_kodu',''))
        y_kutu -= satir_aralik
        yazdir_bilgi(50*mm, y_kutu, "Cari Adı/Ünvanı", cari_bilgi.get('cari_ad_unvan',''))
        y_kutu -= satir_aralik
        yazdir_bilgi(50*mm, y_kutu, "Cari Tipi", cari_bilgi.get('cari_tipi',''))
        y_kutu -= satir_aralik
        yazdir_bilgi(50*mm, y_kutu, "Telefon", cari_bilgi.get('telefon',''))

        # Araç Bilgileri
        y_kutu = y + kutu_yukseklik - 10*mm
        yazdir_bilgi(120*mm, y_kutu, "Araç Bilgileri", "")
        yazdir_bilgi(150*mm, y_kutu, "Plaka", servis_bilgi.get('plaka',''))
        y_kutu -= satir_aralik
        yazdir_bilgi(150*mm, y_kutu, "Tip", arac_bilgi.get('arac_tipi',''))
        y_kutu -= satir_aralik
        yazdir_bilgi(150*mm, y_kutu, "Marka", arac_bilgi.get('marka',''))
        y_kutu -= satir_aralik
        yazdir_bilgi(150*mm, y_kutu, "Model", f"{arac_bilgi.get('model','')}  Yıl: {arac_bilgi.get('model_yili','')}")

        y = y - kutu_yukseklik - 5*mm

        # --- Servis Bilgileri ---
        c.setFont("DejaVu", 11)
        yazdir_bilgi(20*mm, y, "Servis ID", servis_id)
        c.setFont("DejaVu", 10)
        yazdir_bilgi(60*mm, y, "Servis Tarihi", servis_bilgi.get('servis_tarihi',''))
        y -= 8
        aciklama = servis_bilgi.get('aciklama','')
        max_len = 90
        if len(aciklama) > max_len:
            c.drawString(20*mm, y, f"Açıklama: {aciklama[:max_len]}")
            y -= 6
            c.drawString(20*mm, y, f"           {aciklama[max_len:]}")
        else:
            c.drawString(20*mm, y, f"Açıklama: {aciklama}")
        y -= 12

        # --- İşlem Tablosu Başlığı ---
        c.setFont("DejaVu", 11)
        c.setFillColor(colors.gray)
        c.rect(20*mm, y-2*mm, 170*mm, 8*mm, fill=1)
        c.setFillColor(colors.white)
        c.drawString(22*mm, y, "Açıklama")
        c.drawString(80*mm, y, "Tutar")
        c.drawString(110*mm, y, "KDV")
        c.drawString(130*mm, y, "Ek Açıklama")
        c.setFillColor(colors.black)
        y -= 10 * mm

        # --- İşlemler Tablosu ---
        c.setFont("DejaVu", 9)
        toplam_tutar = 0
        for islem in islem_listesi:
            if y < 30 * mm:
                c.showPage()
                y = height - 30 * mm
            _, aciklama, tutar, kdv, ek_aciklama = islem
            c.drawString(22*mm, y, str(aciklama)[:40])
            c.drawString(80*mm, y, f"{tutar:,.2f}")
            c.drawString(110*mm, y, f"%{kdv}")
            c.drawString(130*mm, y, str(ek_aciklama)[:30])
            toplam_tutar += tutar
            y -= 7 * mm

        # --- Toplam Tutar ---
        y -= 5 * mm
        c.setFont("DejaVu", 11)
        c.drawString(22*mm, y, f"Toplam Tutar: {toplam_tutar:,.2f} TL")

        c.save()
        QMessageBox.information(self, "Başarılı", "PDF başarıyla oluşturuldu.")