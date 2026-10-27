from PyQt5.QtWidgets import (
  QDesktopWidget, QDialog, QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDialog, QFileDialog, QMessageBox,
  QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from qtawesome import icon
import sys
from database_progress import load_open_services_with_totals as load_open_services
from arama import eslesir
from service_update import ServiceUpdateForm  # En üste ekleyin
from database_progress import close_service
from servis_form import ServisForm  # <-- Doğru dosya adıyla import
from add_cari import AddCariForm
from database_progress import delete_service  # En üste ekle
from database_progress import get_service_full_details

class OpenServiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Açık Servisler")
        
        # Base resolution for scaling
        BASE_WIDTH = 1366
        BASE_HEIGHT = 768
        
        # Get current screen dimensions
        ekran = QDesktopWidget().screenGeometry()
        self.screen_width = ekran.width()
        self.screen_height = ekran.height()
        
        # Calculate scaling factors
        width_scale = self.screen_width / BASE_WIDTH
        height_scale = self.screen_height / BASE_HEIGHT
        
        # Use the smaller scale to maintain aspect ratio
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        genislik = int(BASE_WIDTH * scale * 0.85)
        yukseklik = int(BASE_HEIGHT * scale * 0.85)
        
        self.resize(genislik, yukseklik)
        x = (self.screen_width - genislik) // 2
        y = (self.screen_height - yukseklik) // 2 - 40
        if y < 0:
            y = 0
        self.move(x, y)
        
        self.init_ui()
        # Initially load all open services
        self.filtrele_servisler()
        self.setWindowIcon(icon('fa5s.file')) # Add a file icon
    def init_ui(self):
        # Ana layout
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(15)

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(10)

        # Buton boyutları için dinamik değerler
        btn_height = int(self.screen_height * 0.035)  # Reduced from 0.04
        btn_width = int(self.screen_width * 0.035)   # Reduced from 0.04
        btn_font_size = int(self.screen_height * 0.012)  # Reduced from 0.014

        btn_servisi_kapat = self.stil_buton("SERVİSİ KAPAT", 'fa5s.check-circle', '#43a047', btn_height, btn_width, btn_font_size)
        btn_yeni_servis = self.stil_buton("YENİ SERVİS GİRİŞİ", 'fa5s.plus-circle', '#0288d1', btn_height, btn_width, btn_font_size)
        btn_kaydi_duzenle = self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#fbc02d', btn_height, btn_width, btn_font_size)
        btn_kaydi_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#f44336', btn_height, btn_width, btn_font_size)
        btn_odeme_al = self.stil_buton("ÖDEME AL", 'fa5s.money-bill', '#43a047', btn_height, btn_width, btn_font_size)
        btn_pdf_aktar = self.stil_buton("PDF AKTAR", 'fa5s.file-pdf', '#0288d1', btn_height, btn_width, btn_font_size)
        btn_sayfayi_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c', btn_height, btn_width, btn_font_size)

        buton_layout.addWidget(btn_servisi_kapat)
        buton_layout.addWidget(btn_yeni_servis)
        buton_layout.addWidget(btn_kaydi_duzenle)
        buton_layout.addWidget(btn_kaydi_sil)
        buton_layout.addWidget(btn_odeme_al)
        buton_layout.addWidget(btn_pdf_aktar)
        buton_layout.addWidget(btn_sayfayi_kapat)

        btn_kaydi_duzenle.clicked.connect(self.kaydi_duzenle)
        btn_servisi_kapat.clicked.connect(self.servisi_kapat)
        btn_yeni_servis.clicked.connect(self.yeni_servis_girisi)
        btn_kaydi_sil.clicked.connect(self.kaydi_sil)
        btn_odeme_al.clicked.connect(self.odeme_al)
        btn_pdf_aktar.clicked.connect(self.pdf_aktar)
        btn_sayfayi_kapat.clicked.connect(self.close)

        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(10)

        # Input alanları için dinamik boyutlar
        input_height = int(self.screen_height * 0.025)  # Reduced from 0.028
        input_font_size = int(self.screen_height * 0.012)  # Reduced from 0.014

        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı, Plaka veya Telefon")
        self.filtre_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: {input_font_size}px;
                padding: {int(input_height * 0.2)}px {int(input_height * 0.3)}px;
                border: 1.5px solid #bbb;
                border-radius: {int(input_height * 0.15)}px;
                background: #fffbe8;
                min-height: {input_height}px;
            }}
        """)
        filtre_layout.addWidget(self.filtre_input)

        btn_filtrele = self.stil_buton("Filtrele", 'fa5s.search', '#1976d2', btn_height, btn_width, btn_font_size)
        btn_temizle = self.stil_buton("Temizle", 'fa5s.sync', '#fbc02d', btn_height, btn_width, btn_font_size)

        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)

        # Connect filter buttons
        btn_filtrele.clicked.connect(self.filtrele_servisler)
        btn_temizle.clicked.connect(self.filtreyi_temizle)
        self.filtre_input.returnPressed.connect(self.filtrele_servisler)
        self.filtre_input.textChanged.connect(self.filtrele_servisler)

        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Servis ID", "Cari Kodu", "Cari Ünvanı", "Plaka", "Tarih", "Tutar", "Aracı Getiren", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                font-size: {int(self.screen_height * 0.016)}px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }}
            QHeaderView::section {{
                background: #ececec;
                font-weight: bold;
                font-size: {int(self.screen_height * 0.016)}px;
                border: 1.5px solid #bbb;
                padding: {int(self.screen_height * 0.013 * 0.4)}px;
            }}
        """)

        ana_layout.addWidget(self.table)

        # Alt bilgi label'ı burada tanımlanıyor
        alt_bilgi_font_size = int(self.screen_height * 0.011)  # Reduced from 0.012
        self.alt_bilgi = QLabel("Kayıtlar listeleniyor...") # Initialize alt_bilgi
        self.alt_bilgi.setStyleSheet(f"""
            font-size: {alt_bilgi_font_size}px;
            color: #444;
            padding: {int(alt_bilgi_font_size * 0.4)}px 0 0 {int(alt_bilgi_font_size * 0.5)}px;
        """)
        ana_layout.addWidget(self.alt_bilgi)

        self.setLayout(ana_layout)

    def stil_buton(self, text, icon_name, color, btn_height, btn_width, btn_font_size):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(btn_height)
        btn.setMinimumWidth(btn_width)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {btn_font_size}px;
                font-weight: bold;
                background: #f5f5f5;
                border: 1.5px solid #bbb;
                border-radius: 6px;
                padding: 18px 18px;
            }}
            QPushButton:hover {{
                background: #e0e0e0;
            }}
        """)
        return btn

    def load_open_services_to_table(self, services):
        """Açık servisleri tabloya yükler ve alt bilgiyi günceller."""
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(len(services))
        toplam_tutar = 0.0

        # Tutar, işlemlerden (KDV dahil) tek sorguda hesaplanmış olarak gelir
        for row, (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi, _telefon) in enumerate(services):
            toplam_tutar_hesaplanan = tutar or 0.0

            self.table.setItem(row, 0, QTableWidgetItem(str(servis_id)))
            self.table.setItem(row, 1, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 2, QTableWidgetItem(cari_unvan))
            self.table.setItem(row, 3, QTableWidgetItem(plaka))
            self.table.setItem(row, 4, QTableWidgetItem(tarih))
            self.table.setItem(row, 5, QTableWidgetItem(f"{toplam_tutar_hesaplanan:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(arac_getiren_kisi or ""))
            self.table.setItem(row, 7, QTableWidgetItem(durum))
            toplam_tutar += toplam_tutar_hesaplanan
        self.table.setUpdatesEnabled(True)

        # Alt bilgiyi güncelle
        alt_bilgi_font_size = int(self.screen_height * 0.011)
        self.alt_bilgi.setText(f"{len(services)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL")
        self.alt_bilgi.setStyleSheet(f"""
            font-size: {alt_bilgi_font_size}px;
            color: #444;
            padding: {int(alt_bilgi_font_size * 0.4)}px 0 0 {int(alt_bilgi_font_size * 0.5)}px;
        """)

    def filtrele_servisler(self):
        """Arama metnine (servis no, cari kodu/adı, plaka, telefon, aracı getiren) göre servisleri listeler."""
        filter_text = self.filtre_input.text()
        # (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi, telefon)
        services = [s for s in load_open_services() if eslesir(filter_text, s[0], s[1], s[2], s[3], s[7], s[8])]
        self.load_open_services_to_table(services)

    def filtreyi_temizle(self):
        """Filtre input alanını temizler ve tüm servisleri listeler."""
        self.filtre_input.clear()
        self.filtrele_servisler() # Load all services again

    def kaydi_duzenle(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_id = self.table.item(selected_row, 0).text()
        details = get_service_full_details(servis_id)
        if not details:
            QMessageBox.warning(self, "Hata", "Servis detayları bulunamadı!")
            return

        # ServiceUpdateForm'u aç ve detayları aktar
        self.servis_update_form = ServiceUpdateForm()
        self.servis_update_form.set_service_details(details)
        result = self.servis_update_form.exec_()
        if result == QDialog.Accepted:
            self.filtrele_servisler() # Update table after edit

    def servisi_kapat(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        # Tablo verilerinden servis ID'sini al
        servis_id = self.table.item(selected_row, 0).text()

        # Servis detaylarını al
        details = get_service_full_details(servis_id)
        if not details:
            QMessageBox.warning(self, "Hata", "Servis detayları bulunamadı!")
            return

        # Toplam tutarı al
        toplam_tutar = details["servis"]["servis_tutar"]

        # Araç çıkış km'sini sor (boş bırakılabilir, iptal edilirse servis kapatılmaz)
        cikis_km = self.cikis_km_sor(details["servis"])
        if cikis_km is False:
            return

        # Servisi kapat ve kapanış tutarını güncelle
        close_service(servis_id, toplam_tutar, cikis_km)

        # Tabloyu güncelle
        self.filtrele_servisler()

        QMessageBox.information(self, "Başarılı", "Servis başarıyla kapatıldı!")

    def cikis_km_sor(self, servis):
        """Çıkış km'sini sorar. Sayı veya boşsa None döndürür; iptal edilirse False."""
        giris_km = servis.get("giris_km")
        mevcut = servis.get("cikis_km")
        while True:
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Servisi Kapat")
            etiket = "Aracın çıkış km'sini giriniz (boş bırakabilirsiniz):"
            if giris_km is not None:
                etiket += f"\nGiriş KM: {giris_km:,}".replace(",", ".")
            dialog.setLabelText(etiket)
            dialog.setTextValue(str(mevcut) if mevcut is not None else "")
            dialog.setOkButtonText("Servisi Kapat")
            dialog.setCancelButtonText("İptal")
            alan = dialog.findChild(QLineEdit)
            if alan:
                alan.setValidator(QIntValidator(0, 9999999, dialog))
            if dialog.exec_() != QDialog.Accepted:
                return False
            metin = dialog.textValue().strip()
            if not metin:
                return None
            try:
                cikis_km = int(metin)
            except ValueError:
                QMessageBox.warning(self, "Uyarı", "Çıkış KM geçerli bir sayı olmalıdır!")
                continue
            if giris_km is not None and cikis_km < giris_km:
                QMessageBox.warning(self, "Uyarı", "Çıkış KM, giriş KM'den küçük olamaz!")
                mevcut = cikis_km
                continue
            return cikis_km

    def yeni_servis_girisi(self):
        self.servis_form = ServisForm()
        result = self.servis_form.exec_()  # Modal olarak aç
        if result == QDialog.Accepted:
            self.filtrele_servisler()  # Yeni servis eklendiyse tabloyu güncelle

    def kaydi_sil(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_id = self.table.item(selected_row, 0).text()

        yanit = QMessageBox.question(self, "Onay", "Seçili servisi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if yanit == QMessageBox.Yes:
            delete_service(servis_id)
            self.filtrele_servisler()
            QMessageBox.information(self, "Başarılı", "Servis kaydı silindi.")

    def odeme_al(self):
        # This method is mentioned in the code but not implemented in the current version
        pass

    def pdf_aktar(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        try:
            servis_id = self.table.item(selected_row, 0).text()
            from pdf_aktar import servis_pdf_aktar
            servis_pdf_aktar(self, servis_id, varsayilan="is_emri")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulurken bir hata oluştu:\n{str(e)}")

    def split_cari_ad_unvan(self, text, max_words=7, max_chars=40):
        """Split customer name into lines for PDF display."""
        words = text.split()
        lines = []
        line_words = []
        line_length = 0

        for word in words:
            line_words.append(word)
            line_length += len(word) + 1
            if len(line_words) == max_words or line_length > max_chars:
                lines.append(' '.join(line_words))
                line_words = []
                line_length = 0

        if line_words:
            lines.append(' '.join(line_words))
        return lines

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = OpenServiceForm()
    form.show()
    sys.exit(app.exec_())