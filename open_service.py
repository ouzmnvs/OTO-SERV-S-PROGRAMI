from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_open_services  # Açık servisleri yüklemek için fonksiyonu içe aktarın
from service_update import ServiceUpdateForm  # En üste ekleyin
from database_progress import close_service  # Servisi kapatmak için fonksiyonu içe aktarın

class OpenServiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Açık Servisler")
        self.init_ui()

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

        btn_kaydi_onayla = self.stil_buton("KAYDI ONAYLA", 'fa5s.check-circle', '#43a047')
        btn_yeni_servis = self.stil_buton("YENİ SERVİS GİRİŞİ", 'fa5s.plus-circle', '#0288d1')
        btn_kaydi_duzenle = self.stil_buton("KAYDI DÜZENLE", 'fa5s.edit', '#fbc02d')
        btn_kaydi_sil = self.stil_buton("KAYDI SİL", 'fa5s.trash', '#b71c1c')
        btn_detay_goruntule = self.stil_buton("DETAY GÖRÜNTÜLE", 'fa5s.info-circle', '#455a64')
        btn_sayfayi_kapat = self.stil_buton("SAYFAYI KAPAT", 'fa5s.times', '#b71c1c')

        buton_layout.addWidget(btn_kaydi_onayla)
        buton_layout.addWidget(btn_yeni_servis)
        buton_layout.addWidget(btn_kaydi_duzenle)
        buton_layout.addWidget(btn_kaydi_sil)
        buton_layout.addWidget(btn_detay_goruntule)
        buton_layout.addWidget(btn_sayfayi_kapat)

        btn_kaydi_duzenle.clicked.connect(self.kaydi_duzenle)  # Bu satırı ekleyin
        btn_kaydi_onayla.clicked.connect(self.kaydi_onayla)  # Bu satırı ekleyin

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

        ana_layout.addLayout(filtre_layout)

        # Tablo
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Servis ID", "Cari Kodu", "Cari Ünvanı", "Plaka", "Tarih", "Tutar"])
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

        # Açık servisleri tabloya yükle
        self.load_open_services_to_table()

        ana_layout.addWidget(self.table)

        # Alt bilgi
        alt_bilgi = QLabel("2 adet kayıt listeleniyor | Toplam Tutar: 750,00 TL")
        alt_bilgi.setStyleSheet("font-size: 14px; color: #444; padding: 6px 0 0 8px;")
        ana_layout.addWidget(alt_bilgi)

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

    def load_open_services_to_table(self):
        """Açık servisleri tabloya yükler."""
        open_services = load_open_services()
        self.table.setRowCount(len(open_services))  # Satır sayısını ayarla

        for row, (servis_id, cari_kodu, cari_unvan, plaka, tarih, tutar, durum) in enumerate(open_services):
            self.table.setItem(row, 0, QTableWidgetItem(str(servis_id)))
            self.table.setItem(row, 1, QTableWidgetItem(cari_kodu))
            self.table.setItem(row, 2, QTableWidgetItem(cari_unvan))
            self.table.setItem(row, 3, QTableWidgetItem(plaka))
            self.table.setItem(row, 4, QTableWidgetItem(tarih))
            self.table.setItem(row, 5, QTableWidgetItem(f"{tutar:.2f}"))

    def kaydi_duzenle(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        # Tablo verilerini al
        servis_id = self.table.item(selected_row, 0).text()
        cari_kodu = self.table.item(selected_row, 1).text()
        cari_unvan = self.table.item(selected_row, 2).text()
        plaka = self.table.item(selected_row, 3).text()

        # Veritabanından ek bilgileri yükle
        from database_progress import load_car_details, load_cari_details, load_service_operations
        cari_details = load_cari_details(cari_kodu)
        car_details = load_car_details(plaka)
        service_operations = load_service_operations(servis_id)

        # ServiceUpdateForm'u aç ve bilgileri aktar
        self.update_form = ServiceUpdateForm()
        self.update_form.txt_cari_kodu.setText(cari_kodu)
        self.update_form.txt_cari_unvan.setText(cari_unvan)
        self.update_form.txt_telefon.setText(cari_details.get("telefon", ""))
        self.update_form.cmb_cari_tipi.setCurrentText(cari_details.get("cari_tipi", ""))
        self.update_form.txt_plaka.setText(plaka)
        self.update_form.cmb_arac_tipi.setCurrentText(car_details.get("arac_tipi", ""))
        self.update_form.txt_model_yili.setText(str(car_details.get("model_yili", "")))
        self.update_form.txt_marka.setText(car_details.get("marka", ""))
        self.update_form.txt_model.setText(car_details.get("model", ""))
        self.update_form.servis_id = int(servis_id)  # Servis ID'sini aktar

        # İşlemleri işlemler tablosuna ekle
        self.update_form.tbl_islemler.setRowCount(len(service_operations))
        for row, (islem_aciklama, islem_tutari, kdv_orani, aciklama) in enumerate(service_operations):
            self.update_form.tbl_islemler.setItem(row, 0, QTableWidgetItem(islem_aciklama))
            self.update_form.tbl_islemler.setItem(row, 1, QTableWidgetItem(f"{islem_tutari:.2f}"))
            self.update_form.tbl_islemler.setItem(row, 2, QTableWidgetItem(f"{kdv_orani:.2f}"))
            self.update_form.tbl_islemler.setItem(row, 3, QTableWidgetItem(aciklama))

        self.update_form.show()

    def kaydi_onayla(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis seçin!")
            return

        # Tablo verilerinden servis ID'sini al
        servis_id = self.table.item(selected_row, 0).text()

        # Servisi kapat
        close_service(servis_id)

        # Tabloyu güncelle
        self.load_open_services_to_table()

        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Başarılı", "Servis başarıyla kapatıldı!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = OpenServiceForm()
    form.show()
    sys.exit(app.exec_())