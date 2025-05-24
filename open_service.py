from PyQt5.QtWidgets import (
   QDialog, QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDialog
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
        self.init_ui()
        # Initially load all open services
        self.load_open_services_to_table(load_open_services())

    def init_ui(self):
        # Ekran boyutlarına göre pencereyi orantılı ayarla
        from PyQt5.QtWidgets import QDesktopWidget
        ekran = QDesktopWidget().screenGeometry()
        genislik = int(ekran.width() * 0.85)
        yukseklik = int(ekran.height() * 0.85)
        self.setFixedSize(genislik, yukseklik)
        x = (ekran.width() - genislik) // 2
        y = (ekran.height() - yukseklik) // 2 - 40
        self.move(x, y)

        # Ana layout
        ana_layout = QVBoxLayout()
        ana_layout.setSpacing(15)

        # Üst butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(10)

        btn_servisi_kapat = self.stil_buton("SERVİSİ KAPAT", 'fa5s.check-circle', '#43a047')
        btn_yeni_servis = self.stil_buton("YENİ SERVİS GİRİŞİ", 'fa5s.plus-circle', '#0288d1')
        btn_kaydi_duzenle = self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#fbc02d')
        btn_kaydi_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_detay_goruntule = self.stil_buton("DETAY GÖRÜNTÜLE", 'fa5s.info-circle', '#455a64')
        btn_sayfayi_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')

        buton_layout.addWidget(btn_servisi_kapat)
        buton_layout.addWidget(btn_yeni_servis)
        buton_layout.addWidget(btn_kaydi_duzenle)
        buton_layout.addWidget(btn_kaydi_sil)
        buton_layout.addWidget(btn_detay_goruntule)
        buton_layout.addWidget(btn_sayfayi_kapat)

        btn_kaydi_duzenle.clicked.connect(self.kaydi_duzenle)
        btn_servisi_kapat.clicked.connect(self.servisi_kapat)
        btn_yeni_servis.clicked.connect(self.yeni_servis_girisi)
        btn_kaydi_sil.clicked.connect(self.kaydi_sil)
        btn_sayfayi_kapat.clicked.connect(self.close)

        ana_layout.addLayout(buton_layout)

        # Filtre alanı
        filtre_layout = QHBoxLayout()
        filtre_layout.setSpacing(10)

        self.filtre_input = QLineEdit()
        self.filtre_input.setPlaceholderText("Cari Kodu, Cari Adı, Plaka veya Telefon")
        self.filtre_input.setStyleSheet("""
            font-size: 16px;
            border: 1.5px solid #bbb;
            border-radius: 6px;
            padding: 8px 12px;
            background: #fffbe8;  /* Sarı arka plan */
        """)
        filtre_layout.addWidget(self.filtre_input)

        btn_filtrele = self.stil_buton("Filtrele", 'fa5s.search', '#1976d2')
        btn_temizle = self.stil_buton("Temizle", 'fa5s.sync', '#fbc02d')

        filtre_layout.addWidget(btn_filtrele)
        filtre_layout.addWidget(btn_temizle)

        # Connect filter buttons
        btn_filtrele.clicked.connect(self.filtrele_servisler)
        btn_temizle.clicked.connect(self.filtreyi_temizle)

        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Servis ID", "Cari Kodu", "Cari Ünvanı", "Plaka", "Tarih", "Tutar", "Aracı Getiren"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 15px;
                alternate-background-color: #f5f5f5;
                background: #fff;
            }
            QHeaderView::section {
                background: #ececec;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #bbb;
                padding: 6px;
            }
        """)

        ana_layout.addWidget(self.table)

        # Alt bilgi label'ı burada tanımlanıyor
        self.alt_bilgi = QLabel("Kayıtlar listeleniyor...") # Initialize alt_bilgi
        self.alt_bilgi.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        ana_layout.addWidget(self.alt_bilgi)

        self.setLayout(ana_layout)

    def stil_buton(self, text, icon_name, color):
        btn = QPushButton(icon(icon_name, color=color), text)
        btn.setMinimumHeight(80)
        btn.setMinimumWidth(80)
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
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
            toplam_tutar += tutar

        # Update the alt_bilgi label
        self.alt_bilgi.setText(f"{len(services)} adet kayıt listeleniyor | Toplam Tutar: {toplam_tutar:.2f} TL")

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
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_id = self.table.item(selected_row, 0).text()
        details = get_service_full_details(servis_id)
        if not details:
            from PyQt5.QtWidgets import QMessageBox
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
            from PyQt5.QtWidgets import QMessageBox
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

        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Başarılı", "Servis başarıyla kapatıldı!")

    def yeni_servis_girisi(self):
        self.servis_form = ServisForm()
        result = self.servis_form.exec_()  # Modal olarak aç
        if result == QDialog.Accepted:
            self.load_open_services_to_table(load_open_services())  # Yeni servis eklendiyse tabloyu güncelle

    def kaydi_sil(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        servis_id = self.table.item(selected_row, 0).text()

        from PyQt5.QtWidgets import QMessageBox
        yanit = QMessageBox.question(self, "Onay", "Seçili servisi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if yanit == QMessageBox.Yes:
            delete_service(servis_id)
            self.load_open_services_to_table(load_open_services())
            QMessageBox.information(self, "Başarılı", "Servis kaydı silindi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = OpenServiceForm()
    form.show()
    sys.exit(app.exec_())