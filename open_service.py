from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from qtawesome import icon
import sys
from database_progress import load_open_services  # Açık servisleri yüklemek için fonksiyonu içe aktarın

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = OpenServiceForm()
    form.show()
    sys.exit(app.exec_())