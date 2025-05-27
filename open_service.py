from PyQt5.QtWidgets import (
  QDesktopWidget, QDialog, QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDialog, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_open_services
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
        self.load_open_services_to_table(load_open_services())
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
        self.table.setRowCount(len(services))  # Satır sayısını ayarla
        toplam_tutar = 0.0

        for row, (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi) in enumerate(services):
            self.table.setItem(row, 0, QTableWidgetItem(str(servis_id)))
            self.table.setItem(row, 1, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 2, QTableWidgetItem(cari_unvan))
            self.table.setItem(row, 3, QTableWidgetItem(plaka))
            self.table.setItem(row, 4, QTableWidgetItem(tarih))
            self.table.setItem(row, 5, QTableWidgetItem(f"{tutar:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(arac_getiren_kisi or ""))
            self.table.setItem(row, 7, QTableWidgetItem(durum))
            toplam_tutar += tutar

        # Update the alt_bilgi label
        alt_bilgi_font_size = int(self.screen_height * 0.011)  # Reduced from 0.012
        self.alt_bilgi.setText(f"{len(services)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL")
        self.alt_bilgi.setStyleSheet(f"""
            font-size: {alt_bilgi_font_size}px;
            color: #444;
            padding: {int(alt_bilgi_font_size * 0.4)}px 0 0 {int(alt_bilgi_font_size * 0.5)}px;
        """)

    def filtrele_servisler(self):
        """Input alanındaki metne göre servisleri filtreler."""
        filter_text = self.filtre_input.text().lower()
        all_services = load_open_services() # Get all services

        if not filter_text:
            self.load_open_services_to_table(all_services) # If no filter, show all
            return

        filtered_services = []
        for service in all_services:
            # service is (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum, arac_getiren_kisi)
            cari_kodu = str(service[1]).lower()
            cari_unvan = str(service[2]).lower()
            plaka = str(service[3]).lower()
            # We need phone number for filtering, but it's not in load_open_services return
            # Assuming phone number is not strictly required for now, or we'd need to join with cariler table in load_open_services
            # For now, filtering only by cari_kodu, cari_unvan, plaka
            if filter_text in cari_kodu or filter_text in cari_unvan or filter_text in plaka:
                 filtered_services.append(service)
            # To add phone number filtering, load_open_services would need to return it, e.g.:
            # load_open_services() -> (..., c.cep_telefonu)
            # Then filter_text in str(service[X]).lower() where X is the phone index

        self.load_open_services_to_table(filtered_services)

    def filtreyi_temizle(self):
        """Filtre input alanını temizler ve tüm servisleri listeler."""
        self.filtre_input.clear()
        self.load_open_services_to_table(load_open_services()) # Load all services again

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
            self.load_open_services_to_table(load_open_services()) # Update table after edit

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

        # Servisi kapat ve kapanış tutarını güncelle
        close_service(servis_id, toplam_tutar)

        # Tabloyu güncelle
        self.load_open_services_to_table(load_open_services())

        QMessageBox.information(self, "Başarılı", "Servis başarıyla kapatıldı!")

    def yeni_servis_girisi(self):
        self.servis_form = ServisForm()
        result = self.servis_form.exec_()  # Modal olarak aç
        if result == QDialog.Accepted:
            self.load_open_services_to_table(load_open_services())  # Yeni servis eklendiyse tabloyu güncelle

    def kaydi_sil(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_id = self.table.item(selected_row, 0).text()

        yanit = QMessageBox.question(self, "Onay", "Seçili servisi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if yanit == QMessageBox.Yes:
            delete_service(servis_id)
            self.load_open_services_to_table(load_open_services())
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
            # Get service ID from the table's UserRole data
            servis_id = self.table.item(selected_row, 0).data(Qt.UserRole)
            if not servis_id:
                servis_id = self.table.item(selected_row, 0).text()
            
            details = get_service_full_details(servis_id)
            if not details:
                QMessageBox.warning(self, "Uyarı", "Servis detayları bulunamadı!")
                return

            # Get service, customer and vehicle information
            servis = details["servis"]
            cari = details["cari"]
            arac = details["arac"]
            islemler = details["islemler"]

            # Format service number to 6 digits
            is_emri_no = f"{int(servis['id']):06d}"

            # İşlemleri PDF için hazırla
            islem_texts = []
            y_start = 155
            line_height = 6

            # İşlemleri benzersiz olarak işle
            processed_operations = set()  # İşlenmiş işlemleri takip etmek için set
            for i, islem in enumerate(islemler, 1):
                # İşlem açıklaması ve miktarını birleştirerek benzersiz bir anahtar oluştur
                operation_key = f"{islem['islem_aciklama']}_{islem['miktar']}"
                
                # Eğer bu işlem daha önce işlenmediyse ekle
                if operation_key not in processed_operations:
                    processed_operations.add(operation_key)
                    islem_texts.extend([
                        (10, y_start - (i * line_height), str(i)),
                        (30, y_start - (i * line_height), f"{islem['islem_aciklama']} {islem['aciklama']}"),
                        (114.5, y_start - (i * line_height), f"{islem['islem_tutari'] / islem['miktar']:.2f}"),  # Birim fiyat = işlem tutarı / miktar
                        (136, y_start - (i * line_height), str(islem['miktar'])),  # Miktar bilgisini ekle
                        (148, y_start - (i * line_height), f"{islem['islem_tutari']:.2f}"),  # Toplam tutar
                        (170, y_start - (i * line_height), f"{islem['kdv_orani']:.1f}%"),  # KDV oranını yüzde olarak göster
                        (184, y_start - (i * line_height), f"{islem['islem_tutari']:.2f}")  # Toplam tutar
                    ])

            # Check tax number
            vergi_no = cari.get('vergi_no', '')
            if vergi_no is None:
                vergi_no = ''

            # Create additions dictionary for PDF
            eklemeler = {
                'text': [
                    (159, 260, is_emri_no),
                    (90, 259.6, f"{servis['plaka']}"),
                ]
            }

            # Split customer name into lines
            cari_ad_unvan = cari.get('cari_ad_unvan', '')
            cari_ad_unvan_lines = self.split_cari_ad_unvan(cari_ad_unvan)

            # Add each line to PDF (font size 7.5 for customer name)
            for i, line in enumerate(cari_ad_unvan_lines):
                eklemeler['text'].append((45, 250 - (i * 5), line, 8))

            # Add other information (font 9)
            eklemeler['text'].extend([
                (50, 237, f"{cari.get('cep_telefonu', '')}", 9),
                (50, 232, f"{vergi_no}", 9),
                (50, 223, f"{arac.get('arac_tipi', '')}", 9),
                (50, 218, f"{arac.get('marka', '')} {arac.get('model', '')}", 9),
                (50, 211, f"{arac.get('model_yili', '')}", 9),
                (120, 223, f"{arac.get('sasi_no', '')}", 9),
                (120, 218, f"{arac.get('motor_no', '')}", 9),
                (58, 204.5, f"{servis['servis_tarihi']}", 9),
                (58, 191.5, f"{servis['servis_tarihi']}", 9),
                (25, 181, f"{servis.get('aciklama', '')}", 9),
                (175, 68, f"{sum(islem['islem_tutari'] for islem in islemler):,.2f} TL", 9),
                (175, 63, f"{sum(islem['kdv_tutari'] for islem in islemler):,.2f} TL", 9),
                (175, 58, f"{sum(islem['islem_tutari'] for islem in islemler):,.2f} TL", 9)
            ])

            # Add operations to additions list (font 9)
            for item in islem_texts:
                if len(item) == 3:
                    eklemeler['text'].append((*item, 9))
                else:
                    eklemeler['text'].append(item)

            # Show save file dialog
            default_filename = f"servis_{is_emri_no}_{servis['plaka']}_{servis['servis_tarihi']}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "PDF Dosyasını Kaydet",
                default_filename,
                "PDF Dosyaları (*.pdf)"
            )

            if file_path:
                # Create PDF
                from pdf_oluşturucu import mevcut_pdf_duzenle
                mevcut_pdf_duzenle("classiccar.pdf", file_path, eklemeler, font_size=10)
                QMessageBox.information(self, "Başarılı", f"PDF dosyası oluşturuldu:\n{file_path}")
            else:
                QMessageBox.information(self, "Bilgi", "PDF oluşturma işlemi iptal edildi.")

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