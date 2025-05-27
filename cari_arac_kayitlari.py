from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QMessageBox
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from qtawesome import icon
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class AracListesiForm(QDialog):
    def __init__(self, cari_kodu, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Araç Listesi")
        self.setFixedSize(600, 400)
        self.cari_kodu = cari_kodu
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Üst butonlar
        buton_layout = QHBoxLayout()
        btn_servis_kayitlari = QPushButton(icon('fa5s.history', color='#1976d2'), "Servis Kayıtları")
        btn_servis_kayitlari.clicked.connect(self.servis_kayitlari_goster)
        buton_layout.addWidget(btn_servis_kayitlari)
        # Detay Görüntüle butonu eklendi
        btn_detay = QPushButton(icon('fa5s.file-alt', color='#1976d2'), "Detay Görüntüle")
        btn_detay.clicked.connect(self.detay_goruntule)
        buton_layout.addWidget(btn_detay)
        buton_layout.addWidget(QPushButton(icon('fa5s.times', color='#b71c1c'), "İptal"))
        buton_layout.addWidget(QPushButton(icon('fa5s.plus-circle', color='#43a047'), "Yeni Ekle"))
        layout.addLayout(buton_layout)

        # Tablo
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Araç Plakası", "Araç Tipi", "Model Yılı", "Marka", "Model", "Son Kapalı Servis Tutarı"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_araclar()

    def load_araclar(self):
        from database_progress import load_car_list_by_cari_with_last_closed_service_info
        araclar = load_car_list_by_cari_with_last_closed_service_info(self.cari_kodu)
        self.table.setRowCount(len(araclar))
        for row, (plaka, arac_tipi, model_yili, marka, model, son_kapali_servis_tutar, son_kapali_servis_tarihi) in enumerate(araclar):
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(arac_tipi))
            self.table.setItem(row, 2, QTableWidgetItem(str(model_yili)))
            self.table.setItem(row, 3, QTableWidgetItem(marka))
            self.table.setItem(row, 4, QTableWidgetItem(model))
            self.table.setItem(row, 5, QTableWidgetItem(f"{son_kapali_servis_tutar:,.2f}" if son_kapali_servis_tutar else "0,00"))

    def servis_kayitlari_goster(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return
        plaka = self.table.item(selected_row, 0).text()
        arac_tipi = self.table.item(selected_row, 1).text()
        model_yili = self.table.item(selected_row, 2).text()
        marka = self.table.item(selected_row, 3).text()
        model = self.table.item(selected_row, 4).text()
        from servis_kayitlari import ServisKayitlariForm
        form = ServisKayitlariForm("", plaka, arac_tipi, model_yili, marka, model, self)
        form.exec_()

    def detay_goruntule(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir araç seçin!")
            return

        plaka = self.table.item(selected_row, 0).text()
        from database_progress import get_last_closed_service_id_by_plaka, load_service_details, load_service_operations, load_cari_details, load_car_details
        servis_id = get_last_closed_service_id_by_plaka(plaka)
        if not servis_id:
            QMessageBox.warning(self, "Uyarı", "Bu araca ait kapalı servis bulunamadı!")
            return

        servis_bilgi = load_service_details(servis_id)
        islem_listesi = load_service_operations(servis_id)
        cari_bilgi = load_cari_details(servis_bilgi.get("cari_kodu", "")) if servis_bilgi else {}
        arac_bilgi = load_car_details(plaka)

        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", f"servis_{servis_id}.pdf", "PDF Files (*.pdf)")
        if not dosya_yolu:
            return

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from reportlab.lib import colors

        c = canvas.Canvas(dosya_yolu, pagesize=A4)
        width, height = A4
        y = height - 25 * mm

        # Başlık
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, y, "SERVİS DETAY RAPORU")
        y -= 15 * mm

        # Cari ve Araç Bilgileri Kutusu
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.lightgrey)
        c.rect(15*mm, y-5*mm, width-30*mm, 30*mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y+20, "Cari Bilgileri:")
        c.setFont("Helvetica", 10)
        c.drawString(50*mm, y+20, f"Cari Kodu: {servis_bilgi.get('cari_kodu','')}")
        c.drawString(50*mm, y+10, f"Cari Tipi: {cari_bilgi.get('cari_tipi','')}")
        c.drawString(50*mm, y, f"Telefon: {cari_bilgi.get('telefon','')}")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(120*mm, y+20, "Araç Bilgileri:")
        c.setFont("Helvetica", 10)
        c.drawString(150*mm, y+20, f"Plaka: {servis_bilgi.get('plaka','')}")
        c.drawString(150*mm, y+10, f"Tip: {arac_bilgi.get('arac_tipi','')}")
        c.drawString(150*mm, y, f"Marka: {arac_bilgi.get('marka','')}  Model: {arac_bilgi.get('model','')}  Yıl: {arac_bilgi.get('model_yili','')}")
        y -= 15 * mm

        # Servis Bilgileri
        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, f"Servis ID: {servis_id}")
        c.setFont("Helvetica", 10)
        c.drawString(60*mm, y, f"Servis Tarihi: {servis_bilgi.get('servis_tarihi','')}")
        y -= 8
        c.drawString(20*mm, y, f"Açıklama: {servis_bilgi.get('aciklama','')}")
        y -= 12

        # İşlem Tablosu Başlığı
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.gray)
        c.rect(20*mm, y-2*mm, 170*mm, 8*mm, fill=1)
        c.setFillColor(colors.white)
        c.drawString(22*mm, y, "Açıklama")
        c.drawString(80*mm, y, "Tutar")
        c.drawString(110*mm, y, "KDV")
        c.drawString(130*mm, y, "Ek Açıklama")
        c.setFillColor(colors.black)
        y -= 10 * mm

        # İşlemler Tablosu
        c.setFont("Helvetica", 10)
        toplam_tutar = 0
        for islem in islem_listesi:
            if y < 30 * mm:
                c.showPage()
                y = height - 30 * mm
            _, aciklama, tutar, kdv, ek_aciklama = islem
            c.drawString(22*mm, y, str(aciklama))
            c.drawString(80*mm, y, f"{tutar:,.2f}")
            c.drawString(110*mm, y, f"%{kdv}")
            c.drawString(130*mm, y, str(ek_aciklama))
            toplam_tutar += tutar
            y -= 7 * mm

        # Toplam Tutar
        y -= 5 * mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(22*mm, y, f"Toplam Tutar: {toplam_tutar:,.2f} TL")

        c.save()
        QMessageBox.information(self, "Başarılı", "PDF başarıyla oluşturuldu.")